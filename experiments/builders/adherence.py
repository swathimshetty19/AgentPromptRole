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


def system_plus_user(
    query_text: str, api_schema_definition: dict[str, Any]
) -> list[Message]:
    schema_str = _format_schema_for_prompt(api_schema_definition)
    return [
        {"role": "system", "content": SYSTEM_PART},
        {
            "role": "user",
            "content": USER_PART.format(schema_str=schema_str, query_text=query_text),
        },
    ]


def user_plus_assistant_seed(
    query_text: str, api_schema_definition: dict[str, Any]
) -> list[Message]:
    schema_str = _format_schema_for_prompt(api_schema_definition)
    return [
        {
            "role": "user",
            "content": (
                SYSTEM_PART
                + USER_PART.format(schema_str=schema_str, query_text=query_text)
            ),
        },
        {"role": "assistant", "content": "{"},
    ]
