from experiments.validators.base_validator import validator_type
from experiments.validators.json_schema import (
    validate_json,
    validate_json_with_pydantic,
)
from experiments.validators.multi_inst_validator import multi_inst_validator


def get_validator(validator: str) -> validator_type:
    """Returns the requested validator function."""
    # NOTE: add new validators here
    if validator == "json_schema_validator":
        return validate_json
    if validator == "pydantic_schema_validator":
        return validate_json_with_pydantic
    if validator == "multi_inst_validator":
        return multi_inst_validator

    raise ValueError(f"Validator '{validator}' not recognized")
