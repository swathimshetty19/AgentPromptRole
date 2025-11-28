"""
Modified ToolBench builders for multi-turn experiments.
Add this file to your experiments/builders/ directory as multi_turn_toolbench.py
"""

import json
from typing import Any
from experiments.models.base_client import Message


SYSTEM_PART = """\
You are a precise API argument extractor. \
You receive a Tool Definition and a User Query. \
You must output a valid JSON object containing the arguments based on the schema. \
Note that you should always output a single JSON object, not a list of JSON objects. \
Do not include markdown formatting. \
"""

USER_PART = """\
### Tool Definition
{schema_str}
### User Query
{query_text}\
"""


def _format_schema_for_prompt(schema: dict[str, Any]) -> str:
    clean_schema = {
        "tool_name": schema.get("tool_name", "UnknownTool"),
        "description": schema.get("api_description", ""),
        "required_parameters": [
            {k: v for k, v in p.items() if k in ["name", "type", "description"]}
            for p in schema.get("required_parameters", [])
        ],
        "optional_parameters": [
            {k: v for k, v in p.items() if k in ["name", "type", "description"]}
            for p in schema.get("optional_parameters", [])
        ],
    }
    return json.dumps(clean_schema, indent=2)


def _build_seed_args(api_schema_definition: dict[str, Any]) -> dict[str, Any]:
    """
    For every parameter name, create a generic seed value:
    name="query" -> "__SEED_QUERY__"
    name="lat"   -> "__SEED_LAT__"
    etc.
    """
    seed_args: dict[str, Any] = {}

    for section in ("required_parameters", "optional_parameters"):
        for p in api_schema_definition.get(section, []) or []:
            name = p.get("name")
            if not name:
                continue
            seed_args[name] = f"__SEED_{name.upper()}__"

    return seed_args


# BASELINE - Same as original toolbench_user_only
def user_only(query_text: str, api_schema_definition: dict[str, Any]) -> list[Message]:
    schema_str = _format_schema_for_prompt(api_schema_definition)
    return [
        {
            "role": "user",
            "content": (
                SYSTEM_PART
                + USER_PART.format(schema_str=schema_str, query_text=query_text)
            ),
        }
    ]


# MULTI-TURN TEST - Assistant demonstrates markdown in previous turn
def user_with_assistant_markdown_history(
    query_text: str, api_schema_definition: dict[str, Any]
) -> list[Message]:
    """
    Multi-turn builder:
    1) user: instructions + schema + dummy seed query
    2) assistant: markdown JSON with generic seed args
    3) user: schema + *real* query (query_text)
    """
    schema_str = _format_schema_for_prompt(api_schema_definition)
    seed_args = _build_seed_args(api_schema_definition)

    # You can keep the dummy query generic; it just exists to create the assistant turn.
    seed_query = "Find cooking videos"

    return [
        {
            "role": "user",
            "content": (
                SYSTEM_PART
                + USER_PART.format(schema_str=schema_str, query_text=seed_query)
            ),
        },
        {
            "role": "assistant",
            "content": "```json\n" + json.dumps(seed_args, indent=2) + "\n```",
        },
        {
            "role": "user",
            "content": USER_PART.format(schema_str=schema_str, query_text=query_text),
        },
    ]


# MULTI-TURN TEST - Assistant adds explanation
def user_with_assistant_explanation_history(
    query_text: str, api_schema_definition: dict[str, Any]
) -> list[Message]:
    """
    Multi-turn variant where the assistant gives a natural-language explanation
    and includes seed (dummy) argument values inside that explanation.
    """
    schema_str = _format_schema_for_prompt(api_schema_definition)

    # --- GENERIC SEED ARGUMENTS FOR THIS TOOL ---
    seed_args = _build_seed_args(api_schema_definition)

    # --- SEED QUERY (any harmless fake request) ---
    seed_query = "Find cooking videos"

    # --- NATURAL LANGUAGE ASSISTANT SEED ---
    assistant_explanation = (
        "Here are the extracted arguments I think you should use:\n\n"
        + json.dumps(seed_args, indent=2)
        + "\n\nLet me know if you'd like me to execute this."
    )

    return [
        # First user message with seed query
        {
            "role": "user",
            "content": (
                SYSTEM_PART
                + USER_PART.format(schema_str=schema_str, query_text=seed_query)
            ),
        },

        # Seed assistant "explanation" containing the dummy arguments
        {
            "role": "assistant",
            "content": assistant_explanation,
        },

        # Final user query — the real one the model SHOULD follow
        {
            "role": "user",
            "content": USER_PART.format(schema_str=schema_str, query_text=query_text),
        },
    ]