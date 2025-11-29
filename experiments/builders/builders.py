from experiments.builders.adherence import (
    system_plus_user as toolbench_system_plus_user,
)
from experiments.builders.adherence import user_only as toolbench_user_only
from experiments.builders.adherence import (
    user_plus_assistant_seed as toolbench_user_plus_assistant_seed,
)
from experiments.builders.multi_turn_inst_builder import (
    user_only as toolbench_multi_turn_user_only,
    user_with_assistant_markdown_history as toolbench_user_with_assistant_markdown_history,
    user_with_assistant_explanation_history as toolbench_user_with_assistant_explanation_history,
)

from experiments.builders.tool_agentic_builder import (
agent_chain_tools, agent_chain_assistant_style
)

from experiments.models.base_client import Message

type builder_type = callable[..., list[Message]]

# NOTE: add new builders here
ALL_BUILDERS: dict[str, builder_type] = {
    "toolbench_user_only": toolbench_user_only,
    "toolbench_system_plus_user": toolbench_system_plus_user,
    "toolbench_user_plus_assistant_seed": toolbench_user_plus_assistant_seed,
    "multi_turn_user_only": toolbench_multi_turn_user_only,
    "multi_turn_user_with_assistant_markdown_history": toolbench_user_with_assistant_markdown_history,
    "multi_turn_user_with_assistant_explanation_history": toolbench_user_with_assistant_explanation_history,
    "agent_chain_tools": agent_chain_tools,
    "agent_chain_assistant_style": agent_chain_assistant_style,
}


def get_builders(variants: list[str]) -> dict[str, builder_type]:
    """Returns the requested builder variants."""
    builders: dict[str, builder_type] = {}
    for variant in variants:
        if variant not in ALL_BUILDERS:
            raise ValueError(f"Variant '{variant}' not recognized")
        builders[variant] = ALL_BUILDERS[variant]

    return builders
