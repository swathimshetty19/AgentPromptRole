import json
import re
from typing import Any, Dict, Optional, Tuple

from experiments.validators.base_validator import ValidatorOutput  # type only

SEED_PATTERN = re.compile(r"^__SEED_[A-Z0-9_]+__$")


def _extract_json_object(raw: str) -> Tuple[Optional[str], Dict[str, Any]]:
    """Try to extract a single JSON object from the raw model output."""
    if raw is None:
        return None, {}

    text = raw.strip()
    if not text:
        return None, {}

    # Try direct parse
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return text, parsed
    except Exception:
        pass

    # Fallback: first {...} block
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return None, {}

    candidate = match.group(0)
    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return candidate, parsed
    except Exception:
        return None, {}

    return None, {}


def _is_seed_value(value: Any) -> bool:
    """Return True if this value looks like one of our generic seed markers."""
    return isinstance(value, str) and SEED_PATTERN.match(value) is not None


def multi_inst_validator(
    output: str,
    api_schema_definition: dict[str, Any],
) -> ValidatorOutput:
    """
    Validator for multi-instruction experiments.

    - Extract a single JSON object
    - Ensure required/optional keys are structurally correct
    - Mark as 'copied seed' if any value matches __SEED_<...>__
    Returns dict: {"valid": bool, "reason": str, "metadata": {...}}
    """

    raw = (output or "").strip()
    if not raw:
        return ValidatorOutput(
            is_valid=False,
            reason="Empty output",
            metadata={"parsed_json": None, "error": "empty"},
        )

    cleaned, parsed = _extract_json_object(raw)
    if cleaned is None:
        return ValidatorOutput(
            is_valid=False,
            reason="No JSON object found",
            metadata={"parsed_json": None, "error": "no_json_object"},
        )

    # ---------- basic schema checks ----------
    required = [
        p["name"]
        for p in api_schema_definition.get("required_parameters", []) or []
        if "name" in p
    ]
    optional = [
        p["name"]
        for p in api_schema_definition.get("optional_parameters", []) or []
        if "name" in p
    ]
    allowed = set(required + optional)

    keys = set(parsed.keys())
    missing = sorted(list(set(required) - keys))
    unknown = sorted(list(keys - allowed))

    metadata: Dict[str, Any] = {"parsed_json": parsed}

    if missing:
        return ValidatorOutput(
            is_valid=False,
            reason=f"Missing required params: {missing}",
            metadata=metadata,
        )

    if unknown:
        return ValidatorOutput(
            is_valid=False,
            reason=f"Unknown params: {unknown}",
            metadata=metadata,
        )

    # ---------- seed-copy detection ----------
    copied_seed_params = []
    for name, value in parsed.items():
        if name not in allowed:
            continue
        if _is_seed_value(value):
            copied_seed_params.append({"parameter": name, "value": value})

    metadata["copied_seed_params"] = copied_seed_params

    if copied_seed_params:
        bad_names = [p["parameter"] for p in copied_seed_params]
        return ValidatorOutput(
            is_valid=False,  # you can keep True and just rely on metadata if you prefer
            reason=f"Output copied assistant seed values for: {bad_names}",
            metadata=metadata,
        )

    # If we got here: structurally OK + did not reuse seed markers
    return ValidatorOutput(
        is_valid=True,
        reason="Valid JSON arguments for schema (no seed markers)",
        metadata=metadata,
    )
