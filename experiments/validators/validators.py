from experiments.validators.base_validator import validator_type
from experiments.validators.json_schema import validate_json


def get_validator(validator: str) -> validator_type:
    """Returns the requested validator function."""
    if validator == "json_schema_validator":
        return validate_json
    raise ValueError(f"Validator '{validator}' not recognized")
