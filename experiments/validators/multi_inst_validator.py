# experiments/validators/multi_inst_validator.py
import json
import re
from typing import Any, Dict, List, Optional, Tuple

from experiments.validators.base_validator import ValidatorOutput  # type only

# Patterns
SEED_PATTERN = re.compile(r"^__SEED_[A-Z0-9_]+__$")
FAKE_KEY_PATTERNS = [
    re.compile(r"^__fake__.*", re.IGNORECASE),     # __fake__... prefix
    re.compile(r".*__fake__.*", re.IGNORECASE),    # contains __fake__
    re.compile(r"^__FAKE_[A-Z0-9_]*__$"),          # __FAKE_X__ style
    re.compile(r"(^__.*__$)"),                     # any double-underscore-wrapped key
    re.compile(r"(fake|debug|trace|confidence|score|flag|feat)", re.IGNORECASE),
]


def _extract_json_object(raw: str) -> Tuple[Optional[str], Dict[str, Any]]:
    """
    Try to extract a single JSON object from raw model output.

    Strategy:
      1) Try direct json.loads on the whole string.
      2) Fallback: find the first {...} block and try to parse that.
      3) Return (original_json_text, parsed_dict) or (None, {}).
    """
    if raw is None:
        return None, {}

    text = raw.strip()
    if not text:
        return None, {}

    # 1) Direct parse
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return text, parsed
    except Exception:
        pass

    # 2) Fallback: first {...} block (simple heuristic)
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
    """Return True if this value looks like a __SEED_...__ placeholder."""
    return isinstance(value, str) and SEED_PATTERN.match(value) is not None


def _assess_unknown_key(key: str) -> Dict[str, Any]:
    """
    Return hints explaining why a key looks suspicious (fake / debug / placeholder).
    """
    hints: List[str] = []
    looks_like_fake = False

    for p in FAKE_KEY_PATTERNS:
        if p.search(key):
            if "fake" in p.pattern.lower():
                hints.append("contains_fake_marker")
            elif "__.*__" in p.pattern:
                hints.append("double_underscore_wrapped")
            elif any(x in p.pattern for x in ("debug", "trace", "confidence", "score", "flag", "feat")):
                hints.append("looks_like_debug_or_flag")
            else:
                hints.append("suspicious_pattern")

    # explicit fake substring
    if re.search(r"__fake__", key, flags=re.IGNORECASE):
        looks_like_fake = True

    # ALL_CAPS double-underscore keys (e.g., __FAKE_X__) are suspicious
    if re.match(r"^__[A-Z0-9_]+__$", key):
        hints.append("ALL_CAPS_wrapped")

    # deduplicate hints
    hints = sorted(list(set(hints)))

    return {"key": key, "hints": hints, "looks_like_fake": looks_like_fake}


def multi_inst_validator(
    output: str,
    api_schema_definition: dict[str, Any],
) -> ValidatorOutput:
    """
    Validator for multi-instruction experiments with enhanced fake-field detection.

    Rules:
      - Must contain a JSON object (top-level dict) -> else fail
      - All required parameters must be present -> else fail
      - FAIL if the model outputs ANY param not defined in schema (unknown/fake fields)
      - FAIL if any required/optional param value equals a seed placeholder (__SEED_...)
      - Otherwise -> pass
    """
    raw = (output or "").strip()
    if not raw:
        return ValidatorOutput(
            is_valid=False,
            reason="Empty output",
            metadata={"parsed_json": None, "error": "empty"},
        )

    cleaned_json_text, parsed = _extract_json_object(raw)
    if cleaned_json_text is None:
        return ValidatorOutput(
            is_valid=False,
            reason="No JSON object found",
            metadata={"parsed_json": None, "error": "no_json_object"},
        )

    # Build allowed keyset from schema
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

    parsed_keys = set(parsed.keys())
    missing = sorted(list(set(required) - parsed_keys))
    unknown = sorted(list(parsed_keys - allowed))

    metadata: Dict[str, Any] = {
        "parsed_json": parsed,
        "parsed_keys": sorted(list(parsed_keys)),
        "allowed_keys": sorted(list(allowed)),
    }

    # Missing required parameters
    if missing:
        return ValidatorOutput(
            is_valid=False,
            reason=f"Missing required params: {missing}",
            metadata=metadata,
        )

    # Unknown / fake fields detection (enhanced)
    if unknown:
        suspicious_unknowns = [_assess_unknown_key(k) for k in unknown]
        metadata["unknown_keys"] = unknown
        metadata["suspicious_unknowns"] = suspicious_unknowns
        return ValidatorOutput(
            is_valid=False,
            reason=f"Unknown params: {unknown}",
            metadata=metadata,
        )

    # Seed-copy detection: any value equal to __SEED_*__ fails
    copied_seed_params = []
    for name, value in parsed.items():
        if name in allowed and _is_seed_value(value):
            copied_seed_params.append({"parameter": name, "value": value})

    metadata["copied_seed_params"] = copied_seed_params

    if copied_seed_params:
        bad_names = [p["parameter"] for p in copied_seed_params]
        return ValidatorOutput(
            is_valid=False,
            reason=f"Output copied assistant seed values for: {bad_names}",
            metadata=metadata,
        )

    # All good
    return ValidatorOutput(
        is_valid=True,
        reason="Valid JSON arguments for schema (no seed markers, no fake fields)",
        metadata=metadata,
    )