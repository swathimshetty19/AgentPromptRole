from typing import Any, Callable

from typing_extensions import TypedDict


class ValidatorOutput(TypedDict):
    is_valid: bool
    reason: str
    metadata: dict[str, Any]


validator_type = Callable[[str, ...], ValidatorOutput]
