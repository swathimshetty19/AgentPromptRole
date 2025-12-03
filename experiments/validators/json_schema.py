import json
import re
from types import SimpleNamespace
from typing import Any, Dict, List, Literal, Optional, Tuple, Type, Union

import jsonschema
from pydantic import BaseModel, Field, ValidationError, create_model

from experiments.validators.base_validator import ValidatorOutput

# Type mapping
TYPE_MAPPING = {
    "STRING": str,
    "INTEGER": int,
    "NUMBER": float,
    "BOOLEAN": bool,
    "ARRAY": list,
    "OBJECT": dict,
}


def _get_python_type(type_str: str) -> Type:
    return TYPE_MAPPING.get(type_str.upper(), str)  # Default to str if unknown


def generate_dynamic_model(schema_def: Dict[str, Any]) -> Type[BaseModel]:
    model_fields = {}

    for param in schema_def.get("required_parameters", []):
        p_name = param["name"]
        p_type = _get_python_type(param.get("type", "STRING"))
        description = param.get("description", "")

        model_fields[p_name] = (p_type, Field(..., description=description))

    for param in schema_def.get("optional_parameters", []):
        p_name = param["name"]
        p_type = _get_python_type(param.get("type", "STRING"))
        description = param.get("description", "")

        model_fields[p_name] = (
            Optional[p_type],
            Field(default=None, description=description),
        )

    model_name = schema_def.get("api_name", "DynamicToolModel")
    DynamicModel = create_model(model_name, **model_fields)

    return DynamicModel


def validate_json_with_pydantic(output: str, api_schema_definition) -> ValidatorOutput:

    if isinstance(output, str):
        s = output
    elif isinstance(output, list):
        if all(isinstance(x, str) for x in output):
            s = "".join(output)
        else:
            s = json.dumps(output, ensure_ascii=False)
    elif isinstance(output, dict):
        s = json.dumps(output, ensure_ascii=False)
    elif output is None:
        s = ""
    else:
        s = str(output)

    original_length = len(s)
    original_cleaned = s.strip()
    original_length = len(s)
    original_cleaned = s.strip()

    try:
        cleaned = original_cleaned

        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip()

        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        if cleaned.endswith("```"):
            cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

        json_start = cleaned.find("{")
        json_end = cleaned.rfind("}")

        if json_start == -1 or json_end == -1 or json_end <= json_start:
            json_start = cleaned.find("[")
            json_end = cleaned.rfind("]")
            if json_start == -1 or json_end == -1 or json_end <= json_start:
                raise ValueError("No valid JSON structure found")

        json_only = cleaned[json_start : json_end + 1]

        text_before = cleaned[:json_start].strip()
        text_after = cleaned[json_end + 1 :].strip()
        extraneous_chars = len(text_before) + len(text_after)
        extraneous_pct = (
            (extraneous_chars / original_length * 100) if original_length > 0 else 0
        )

        pydantic_model = generate_dynamic_model(api_schema_definition)

        # 3. Validate Logic
        # This checks:
        # - Are all required fields present?
        # - Are the types correct (e.g. int is int)?
        data = json.loads(json_only)
        # print("===DATA===")
        # print(data)
        # pydantic_model.model_validate(data)
        validated_obj = pydantic_model.model_validate(data)

        return ValidatorOutput(
            is_valid=True,
            reason="",
            metadata={
                "extraneous_text_pct": extraneous_pct,
                "cleaned_json_length": len(json_only),
                "original_length": original_length,
            },
        )
    except Exception as e:
        cleaned_for_ex = locals().get("cleaned", s)

        extraneous_pct = 0
        try:
            json_start = cleaned_for_ex.find("{")
            if json_start == -1:
                json_start = cleaned_for_ex.find("[")
            if json_start != -1:
                json_end = cleaned_for_ex.rfind("}")
                if json_end <= json_start:
                    json_end = cleaned_for_ex.rfind("]")
                if json_end > json_start:
                    extraneous_chars = len(cleaned_for_ex[:json_start].strip()) + len(
                        cleaned_for_ex[json_end + 1 :].strip()
                    )
                    extraneous_pct = (
                        (extraneous_chars / original_length * 100)
                        if original_length > 0
                        else 100
                    )
                else:
                    extraneous_pct = 100
            else:
                extraneous_pct = 100
        except:
            extraneous_pct = 100

        return ValidatorOutput(
            is_valid=False,
            reason=str(e),
            metadata={
                "extraneous_text_pct": extraneous_pct,
                "cleaned_json_length": 0,
                "original_length": original_length,
            },
        )


def validate_json(output: Any, schema: dict[str, Any]) -> ValidatorOutput:
    if isinstance(output, str):
        s = output
    elif isinstance(output, list):
        if all(isinstance(x, str) for x in output):
            s = "".join(output)
        else:
            s = json.dumps(output, ensure_ascii=False)
    elif isinstance(output, dict):
        s = json.dumps(output, ensure_ascii=False)
    elif output is None:
        s = ""
    else:
        s = str(output)

    original_length = len(s)
    original_cleaned = s.strip()

    try:
        cleaned = original_cleaned

        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip()

        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        if cleaned.endswith("```"):
            cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

        json_start = cleaned.find("{")
        json_end = cleaned.rfind("}")

        if json_start == -1 or json_end == -1 or json_end <= json_start:
            json_start = cleaned.find("[")
            json_end = cleaned.rfind("]")
            if json_start == -1 or json_end == -1 or json_end <= json_start:
                raise ValueError("No valid JSON structure found")

        json_only = cleaned[json_start : json_end + 1]

        text_before = cleaned[:json_start].strip()
        text_after = cleaned[json_end + 1 :].strip()
        extraneous_chars = len(text_before) + len(text_after)
        extraneous_pct = (
            (extraneous_chars / original_length * 100) if original_length > 0 else 0
        )

        data = json.loads(json_only)
        jsonschema.validate(data, schema)

        return ValidatorOutput(
            is_valid=True,
            reason="",
            metadata={
                "extraneous_text_pct": extraneous_pct,
                "cleaned_json_length": len(json_only),
                "original_length": original_length,
            },
        )
    except Exception as e:
        cleaned_for_ex = locals().get("cleaned", s)

        extraneous_pct = 0
        try:
            json_start = cleaned_for_ex.find("{")
            if json_start == -1:
                json_start = cleaned_for_ex.find("[")
            if json_start != -1:
                json_end = cleaned_for_ex.rfind("}")
                if json_end <= json_start:
                    json_end = cleaned_for_ex.rfind("]")
                if json_end > json_start:
                    extraneous_chars = len(cleaned_for_ex[:json_start].strip()) + len(
                        cleaned_for_ex[json_end + 1 :].strip()
                    )
                    extraneous_pct = (
                        (extraneous_chars / original_length * 100)
                        if original_length > 0
                        else 100
                    )
                else:
                    extraneous_pct = 100
            else:
                extraneous_pct = 100
        except:
            extraneous_pct = 100

        return ValidatorOutput(
            is_valid=False,
            reason=str(e),
            metadata={
                "extraneous_text_pct": extraneous_pct,
                "cleaned_json_length": 0,
                "original_length": original_length,
            },
        )
