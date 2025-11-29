# builder.py
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
        # support backwards-compatible place to pass prior tool calls
        "prior_tool_calls": schema.get("prior_tool_calls", []),
    }
    return json.dumps(clean_schema, indent=2)


def user_only(query_text: str, api_schema_definition: dict[str, Any]) -> list[Message]:
    """
    Single user message containing the system instructions + user payload.
    (Same signature as your original builder)
    """
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
    """
    System message with instructions and a user message containing the schema+query.
    """
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
    """
    User message + an assistant "seed" (simulates an agent assistant partial reply).
    This often triggers models to output a JSON continuation.
    """
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


def agent_chain_tools(
    query_text: str, api_schema_definition: dict[str, Any]
) -> list[Message]:
    """
    Replay prior tool calls as explicit tool messages, then ask the model to decide
    the next tool to call.

    The dataset may include prior tool calls inside api_schema_definition under key
    'prior_tool_calls' as a list of strings (tool names in the order they were called).

    Example:
      api_schema_definition["prior_tool_calls"] = ["Find_cool_countries", "Check_food"]

    Final assistant message prompts the model to return the next tool name (plain text or JSON).
    """
    schema_str = _format_schema_for_prompt(api_schema_definition)
    prior_calls = api_schema_definition.get("prior_tool_calls", []) or []

    messages: list[Message] = []
    # system defines the role and objective
    system_text = (
        "You are an LLM agent that must decide the next tool call given the user query and prior tool outputs.\n"
        "Only choose from the provided tool names.\n"
        + SYSTEM_PART
    )
    messages.append({"role": "system", "content": system_text})

    # user contains the original query + tool schema metadata
    messages.append(
        {
            "role": "user",
            "content": USER_PART.format(schema_str=schema_str, query_text=query_text),
        }
    )

    # replay prior tool calls as tool messages (raw, assume they succeeded)
    for i, tool_name in enumerate(prior_calls):
        # assistant memory update summarizing that tool call
        messages.append({"role": "assistant", "content": f"Memory Update: tool_called={tool_name}"})

    # final assistant prompt: ask for the next tool name
    messages.append({"role": "assistant", "content": "Current State: given the above tool calls, provide the NEXT tool name to call. Only reply with the tool name (or a tiny JSON like {\"tool\":\"ToolName\"})."})
    return messages


def agent_chain_assistant_style(
    query_text: str, api_schema_definition: dict[str, Any]
) -> list[Message]:
    """
    Replay prior tool calls as alternating assistant messages (no 'tool' role).
    This matches the 'Prompt 2' example where prior steps are shown as assistant messages.
    """
    schema_str = _format_schema_for_prompt(api_schema_definition)
    prior_calls = api_schema_definition.get("prior_tool_calls", []) or []

    messages: list[Message] = []
    system_text = (
        "You are an LLM agent that must decide the next tool call given the user query and prior assistant-tool steps.\n"
        "Assume each listed assistant line corresponds to a successful tool call and you have its answer.\n"
        "Only choose from the provided tool names.\n"
        + SYSTEM_PART
    )
    messages.append({"role": "system", "content": system_text})
    messages.append(
        {
            "role": "user",
            "content": USER_PART.format(schema_str=schema_str, query_text=query_text),
        }
    )

    for tool_name in prior_calls:
        messages.append({"role": "assistant", "content": f"ToolCall: {tool_name}"})

    messages.append({"role": "assistant", "content": "Current State: provide the NEXT tool name to call."})
    return messages
