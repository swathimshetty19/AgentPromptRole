from experiments.builders.toolbench import (
    system_plus_user as toolbench_system_plus_user,
)
from experiments.builders.toolbench import user_only as toolbench_user_only
from experiments.builders.toolbench import (
    user_plus_assistant_seed as toolbench_user_plus_assistant_seed,
)
from experiments.models.base_client import Message

type builder_type = callable[..., list[Message]]

# NOTE: add new builders here
ALL_BUILDERS: dict[str, builder_type] = {
    "toolbench_user_only": toolbench_user_only,
    "toolbench_system_plus_user": toolbench_system_plus_user,
    "toolbench_user_plus_assistant_seed": toolbench_user_plus_assistant_seed,
}


def get_builders(variants: list[str]) -> dict[str, builder_type]:
    """Returns the requested builder variants."""
    builders: dict[str, builder_type] = {}
    for variant in variants:
        if variant not in ALL_BUILDERS:
            raise ValueError(f"Variant '{variant}' not recognized")
        builders[variant] = ALL_BUILDERS[variant]

    return builders
