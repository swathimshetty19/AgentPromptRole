from typing import Any

from typing_extensions import TypedDict


class ValidatorOutput(TypedDict):
    is_valid: bool
    reason: str
    metadata: dict[str, Any]


type validator_type = callable[[str, ...], ValidatorOutput]
