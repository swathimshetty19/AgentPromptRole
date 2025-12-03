import json
from typing import Any, Dict, Optional

from experiments.validators.base_validator import ValidatorOutput

# -------------------------------------------------------
# helpers - unchanged from your implementation
# -------------------------------------------------------


def _extract_tool_from_dict(obj: Dict[str, Any]) -> Optional[str]:
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
    Also handles nested structures and filters out placeholder values.
    """
    # First, try direct keys
    for key in ("tool_name", "name", "action", "tool"):
        if key in obj:
            value = obj[key]
            if isinstance(value, str) and value.strip():
                value = value.strip()
                # Skip placeholder values
                if value != "_name" and not value.startswith("_"):
                    return value
    
    # Try nested structures (e.g., {"arguments": {"tool_name": "X"}})
    for key in ("arguments", "parameters", "params", "data"):
        if key in obj and isinstance(obj[key], dict):
            nested_result = _extract_tool_from_dict(obj[key])
            if nested_result:
                return nested_result
    
    # Try to find any string value that looks like a tool name
    # (longer strings, contains spaces/hyphens, not just single words)
    for key, value in obj.items():
        if isinstance(value, str) and len(value) > 3:
            # Skip if it's clearly a parameter value (too long, contains URLs, etc.)
            if "http" not in value.lower() and len(value) < 100:
                # Check if it looks like a tool name (has spaces, hyphens, or is a reasonable length)
                if " " in value or "-" in value or (len(value) > 5 and value.replace(" ", "").replace("-", "").isalnum()):
                    if value != "_name" and not value.startswith("_"):
                        return value.strip()
    
    return None


def _extract_tool_from_json_text(text: str) -> Optional[str]:
    """
    Try:
    1. Clean markdown code blocks
    2. JSON parse (single or multiple JSON objects)
    3. Extract from nested structures
    4. Fallback regex
    5. Keyword heuristics
    """
    import re
    
    text = text.strip()
    
    # Remove markdown code blocks if present
    text = re.sub(r"^```(?:json)?\s*\n?", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n?```\s*$", "", text, flags=re.MULTILINE)
    text = text.strip()

    # Try parsing as JSON (handle single or multiple JSON objects)
    try:
        # Try parsing the whole text
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            result = _extract_tool_from_dict(parsed)
            if result:
                return result
        if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):
            result = _extract_tool_from_dict(parsed[0])
            if result:
                return result
    except json.JSONDecodeError:
        # Try to find and parse first JSON object in text
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text)
        if json_match:
            try:
                parsed = json.loads(json_match.group(0))
                if isinstance(parsed, dict):
                    result = _extract_tool_from_dict(parsed)
                    if result:
                        return result
            except Exception:
                pass

    # Handle cases where GPT outputs full parameter JSON - try to find tool_name in nested structures
    # Look for patterns like {"tool_name": "...", ...} or {"name": "...", ...}
    tool_name_patterns = [
        r'"tool_name"\s*:\s*"([^"]+)"',
        r'"name"\s*:\s*"([^"]+)"',
        r'"tool"\s*:\s*"([^"]+)"',
        r'"action"\s*:\s*"([^"]+)"',
    ]
    for pattern in tool_name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            tool_name = match.group(1).strip()
            # Skip if it's a generic placeholder like "_name"
            if tool_name and tool_name != "_name" and not tool_name.startswith("_"):
                return tool_name

    # Regex extraction (Tool: X or just tool name)
    m = re.search(r"(?i)(?:tool|call|invoke|action)\s*:?\s*([A-Za-z0-9_\- ]+)", text)
    if m:
        tool_name = m.group(1).strip()
        if tool_name != "_name" and not tool_name.startswith("_"):
            return tool_name

    # If output looks like just a tool name (short, no special chars except spaces/hyphens)
    if len(text.split()) <= 5 and re.match(r'^[A-Za-z0-9_\- ]+$', text):
        # Skip if it's a placeholder
        if text != "_name" and not text.startswith("_"):
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
        "raw_preview": None,
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
            is_valid=False,
            reason="No tool name could be parsed from model output",
            metadata=metadata,
        )

    found_norm = found.strip().lower()

    # done-case
    if (
        expected_norm in ("done", "finish", "finished", "complete")
        or expected_norm == ""
    ):
        if found_norm in (
            "done",
            "finish",
            "finished",
            "complete",
            "no_action",
            "no_more",
            "no_more_actions",
        ):
            return ValidatorOutput(
                is_valid=True,
                reason="Correctly indicated done",
                metadata=metadata,
            )
        return ValidatorOutput(
            is_valid=False,
            reason=f"Expected done but model returned '{found}'",
            metadata=metadata,
        )

    # normal case
    if found_norm == expected_norm:
        return ValidatorOutput(
            is_valid=True,
            reason=f"Model called expected tool '{expected_tool}'",
            metadata=metadata,
        )

    return ValidatorOutput(
        is_valid=False,
        reason=f"Model called '{found}' but expected '{expected_tool}'",
        metadata=metadata,
    )


# -------------------------------------------------------
# FINAL PUBLIC VALIDATOR ENTRYPOINT
# -------------------------------------------------------


def agentic_tool_validator(
    output: Any, api_schema_definition: Dict[str, Any]
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
            is_valid=False,
            reason="api_schema_definition is not a dict",
            metadata={"api_schema": str(api_schema_definition)},
        )

    # 🔥 The expected tool is directly from dataset
    expected_tool = api_schema_definition.get("tool_name", "")

    # If dataset indicates termination (rare), handle here if needed
    if expected_tool is None:
        expected_tool = ""

    return tool_name_validator(output, expected_tool)
