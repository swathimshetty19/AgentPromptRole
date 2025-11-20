from experiments.validators.base_validator import validator_type
from experiments.validators.json_schema import (
    validate_json,
    validate_json_with_pydantic,
)


def get_validator(validator: str) -> validator_type:
    """Returns the requested validator function."""
    # NOTE: add new validators here
    if validator == "json_schema_validator":
        return validate_json
    if validator == "pydantic_schema_validator":
        return validate_json_with_pydantic

    raise ValueError(f"Validator '{validator}' not recognized")
