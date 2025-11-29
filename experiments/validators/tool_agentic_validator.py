import json
from typing import Any, Dict

from experiments.validators.base_validator import ValidatorOutput

# -------------------------------------------------------
# helpers - unchanged from your implementation
# -------------------------------------------------------

def _extract_tool_from_dict(obj: Dict[str, Any]) -> str | None:
    """
    Extract a tool name from dict forms such as:
    {
        "tool_name": "X",
        "parameters": {...}
    }
    Or:
    {
        "name": "X",
        "arguments": {...}
    }
    Or assistant-style traces:
    {
        "action": "X",
        "tool": "X"
    }
    """
    for key in ("tool_name", "name", "action", "tool"):
        if key in obj and isinstance(obj[key], str):
            return obj[key]
    return None


def _extract_tool_from_json_text(text: str) -> str | None:
    """
    Try:
    1. JSON parse
    2. Fallback regex
    3. Keyword heuristics
    """
    text = text.strip()

    # Try JSON first
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return _extract_tool_from_dict(parsed)
        if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):
            return _extract_tool_from_dict(parsed[0])
    except Exception:
        pass

    # Regex extraction (Tool: X)
    import re
    m = re.search(
        r"(?i)(?:tool|call|invoke|action)\s*:?\s*([A-Za-z0-9_\- ]+)",
        text
    )
    if m:
        return m.group(1).strip()

    # If output is literally the tool name
    if len(text.split()) <= 3:
        return text.strip()

    return None


# -------------------------------------------------------
# core validator logic (your function, unchanged)
# -------------------------------------------------------

def tool_name_validator(
    output: Any,
    expected_tool: str,
) -> ValidatorOutput:

    expected_norm = (expected_tool or "").strip().lower()

    metadata: Dict[str, Any] = {
        "parsed_tool": None,
        "parsed_by": None,
        "raw_preview": None
    }

    # Case 1: Direct dict
    if isinstance(output, dict):
        found = _extract_tool_from_dict(output)
        metadata["parsed_by"] = "dict"
        metadata["raw_preview"] = json.dumps(output)[:1000]

    # Case 2: List
    elif isinstance(output, list):
        first = output[0] if output else None
        if isinstance(first, dict):
            found = _extract_tool_from_dict(first)
            metadata["parsed_by"] = "list->dict"
            metadata["raw_preview"] = json.dumps(first)[:1000]
        else:
            raw_text = json.dumps(output)
            found = _extract_tool_from_json_text(raw_text)
            metadata["parsed_by"] = "list->text"
            metadata["raw_preview"] = raw_text[:1000]

    # Case 3: String
    else:
        raw_text = "" if output is None else str(output)
        metadata["parsed_by"] = "text"
        metadata["raw_preview"] = raw_text[:1000]
        found = _extract_tool_from_json_text(raw_text)

    metadata["parsed_tool"] = found

    if not found:
        return ValidatorOutput(
            valid=False,
            reason="No tool name could be parsed from model output",
            metadata=metadata,
        )

    found_norm = found.strip().lower()

    # done-case
    if expected_norm in ("done", "finish", "finished", "complete") or expected_norm == "":
        if found_norm in (
            "done", "finish", "finished", "complete",
            "no_action", "no_more", "no_more_actions"
        ):
            return ValidatorOutput(
                valid=True,
                reason="Correctly indicated done",
                metadata=metadata,
            )
        return ValidatorOutput(
            valid=False,
            reason=f"Expected done but model returned '{found}'",
            metadata=metadata,
        )

    # normal case
    if found_norm == expected_norm:
        return ValidatorOutput(
            valid=True,
            reason=f"Model called expected tool '{expected_tool}'",
            metadata=metadata,
        )

    return ValidatorOutput(
        valid=False,
        reason=f"Model called '{found}' but expected '{expected_tool}'",
        metadata=metadata,
    )


# -------------------------------------------------------
# FINAL PUBLIC VALIDATOR ENTRYPOINT
# -------------------------------------------------------

def agentic_tool_validator(
    output: Any,
    api_schema_definition: Dict[str, Any]
) -> ValidatorOutput:
    """
    FINAL validator used by main.py

    Receives:
        output:  LLM string/dict/list
        api_schema_definition: dataset schema that includes tool_name

    Behavior:
        Extract expected tool from api_schema_definition["tool_name"]
        Then validate the LLM output against that tool.
    """

    if not isinstance(api_schema_definition, dict):
        return ValidatorOutput(
            valid=False,
            reason="api_schema_definition is not a dict",
            metadata={"api_schema": str(api_schema_definition)}
        )

    # 🔥 The expected tool is directly from dataset
    expected_tool = api_schema_definition.get("tool_name", "")

    # If dataset indicates termination (rare), handle here if needed
    if expected_tool is None:
        expected_tool = ""

    return tool_name_validator(output, expected_tool)
