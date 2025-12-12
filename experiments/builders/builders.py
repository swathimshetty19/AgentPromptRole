from experiments.builders.adherence import (
    system_plus_user as toolbench_system_plus_user,
)
from experiments.builders.adherence import user_only as toolbench_user_only
from experiments.builders.adherence import (
    user_plus_assistant_seed as toolbench_user_plus_assistant_seed,
)
from experiments.builders.adversary import system_only as adversary_system_only
from experiments.builders.adversary import (
    system_plus_user as adversary_system_plus_user,
)
from experiments.builders.adversary import user_only as adversary_user_only
from experiments.builders.multi_turn_inst_builder import (
    user_only as toolbench_multi_turn_user_only,
)
from experiments.builders.multi_turn_inst_builder import (
    user_with_assistant_explanation_history as toolbench_user_with_assistant_explanation_history,
)
from experiments.builders.multi_turn_inst_builder import (
    user_with_assistant_markdown_history as toolbench_user_with_assistant_markdown_history,
)
from experiments.builders.multi_turn_inst_builder import (
    user_with_assistant_extra_fake_fields as toolbench_user_with_assistant_extra_fake_fields,
)
from experiments.builders.tool_agentic_builder import (
    agent_chain_assistant_style,
    agent_chain_tools,
)
from typing import Callable
from experiments.models.base_client import Message

builder_type = Callable[..., list[Message]]

# NOTE: add new builders here
ALL_BUILDERS: dict[str, builder_type] = {
    "toolbench_user_only": toolbench_user_only,
    "toolbench_system_plus_user": toolbench_system_plus_user,
    "toolbench_user_plus_assistant_seed": toolbench_user_plus_assistant_seed,
    "adversary_user_only": adversary_user_only,
    "adversary_system_only": adversary_system_only,
    "adversary_system_plus_user": adversary_system_plus_user,
    "multi_turn_user_only": toolbench_multi_turn_user_only,
    "multi_turn_user_with_assistant_markdown_history": toolbench_user_with_assistant_markdown_history,
    "multi_turn_user_with_assistant_explanation_history": toolbench_user_with_assistant_explanation_history,
    "multi_turn_user_with_assistant_extra_fake_fields": toolbench_user_with_assistant_extra_fake_fields,
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
