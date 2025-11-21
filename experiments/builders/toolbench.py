import json
from typing import Any

from experiments.models.base_client import Message

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
        ]
    }
    return json.dumps(clean_schema, indent=2)


def user_only(query_text: str, api_schema_definition: dict[str, Any]):
    schema_str = _format_schema_for_prompt(api_schema_definition)

    prompt = (
        f"You are a helpful API calling assistant.\n\n"
        f"### Tool Definition\n{schema_str}\n\n"
        f"### Task\nExtract parameters from the user query below into a valid JSON object based on the tool definition above. "
        f"Ensure all 'required_parameters' are present.\n\n"
        f"### User Query\n{query_text}\n\n"
        f"### Output\nReturn ONLY the JSON object."
    )

    return [{"role": "user", "content": prompt}]


def system_plus_user(query_text: str, api_schema_definition: dict[str, Any]):
    schema_str = _format_schema_for_prompt(api_schema_definition)

    system_prompt = (
        f"You are a precise API argument extractor. You receive a Tool Definition and a User Query. "
        f"You must output a valid JSON object containing the arguments based on the schema. "
        f"Do not include markdown formatting."
    )

    user_prompt = (
        f"### Tool Definition\n{schema_str}\n\n"
        f"### User Query\n{query_text}"
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def user_plus_assistant_seed(query_text: str, api_schema_definition: dict[str, Any]):
    schema_str = _format_schema_for_prompt(api_schema_definition)

    user_prompt = (
        f"Extract the parameters for the following tool based on the query.\n\n"
        f"Schema:\n{schema_str}\n\n"
        f"Query: {query_text}\n\n"
        f"Output JSON:"
    )

    return [
        {"role": "user", "content": user_prompt},
        {"role": "assistant", "content": "{"},
    ]
