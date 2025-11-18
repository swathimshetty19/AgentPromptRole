import json
from typing import Any

from experiments.models.base_client import Message


def user_only(task: str, schema: dict[str, Any], text: str):

    schema_str = json.dumps({
        "required_parameters": schema.get("required_parameters", []),
        "optional_parameters": schema.get("optional_parameters", []),
    }, indent=2)


    return [
        {
            "role": "user",
            "content": (
                f"{task}\nYour output must be valid JSON:\n{schema_str}\nInput: {text}\nOnly return JSON."
            ),
        }
    ]


def system_plus_user(task: str, schema: dict[str, Any], text: str):
    schema_str = json.dumps({
        "required_parameters": schema.get("required_parameters", []),
        "optional_parameters": schema.get("optional_parameters", []),
    }, indent=2)

    return [
        {"role": "system", "content": f"You only output JSON. Schema:\n{schema_str}"},
        {"role": "user", "content": f"{task}\nInput: {text}\nReturn JSON only."},
    ]


def user_plus_assistant_seed(
    task: str, schema: dict[str, Any], text: str
):
    schema_str = json.dumps({
        "required_parameters": schema.get("required_parameters", []),
        "optional_parameters": schema.get("optional_parameters", []),
    }, indent=2)

    return [
        {
            "role": "user",
            "content": f"{task}\nSchema:\n{schema_str}\nInput: {text}\nOnly JSON.",
        },
        {"role": "assistant", "content": "{"},
    ]
