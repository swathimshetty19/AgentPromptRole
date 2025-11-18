import json
import re
from typing import Any
from types import SimpleNamespace

import jsonschema

from experiments.validators.base_validator import ValidatorOutput
from pydantic import BaseModel, create_model, ValidationError
from typing import List, Dict, Any, Optional, Tuple, Type, Union, Literal


def generate_pydantic_model_from_schema(model_name: str) -> Type[BaseModel]:
    "build pydantic schema for validator"
    class Parameter(BaseModel):
        name: str
        type: str
        description: str
        default: Union[str, int, bool, None] = None

        # @model_validator(mode="after")
        # def check_default_type(self):
        #     """Ensure the default value matches the declared 'type'."""
        #     if self.default is None or self.default == "":
        #         return self
        #     if self.type == "STRING" and not isinstance(self.default, str):
        #         raise ValueError("Default must be a string for STRING type.")
        #     if self.type == "NUMBER" and not isinstance(self.default, (int, float)):
        #         raise ValueError("Default must be numeric for NUMBER type.")
        #     if self.type == "BOOLEAN" and not isinstance(self.default, bool):
        #         raise ValueError("Default must be a boolean for BOOLEAN type.")
        #     return self

    class SchemaModel(BaseModel):
        required_parameters: List[Parameter]
        optional_parameters: List[Parameter]

    safe_model_name = "".join(c for c in model_name if c.isalnum() or c == "_")
    if not safe_model_name.isidentifier():
        safe_model_name = "GeneratedPydanticModel"

    return create_model(safe_model_name, __base__=SchemaModel)

def safe_json_loads(s: str):
    s = re.sub(r"```(?:json)?", "", s).strip()

    def fix_newlines(match):
        return match.group(0).replace("\n", "\\n")

    s = re.sub(r'"(?:[^"\\]|\\.)*"', fix_newlines, s)
    return json.loads(s)

def validate_json_with_pydantic(output: str, model_name) -> ValidatorOutput:

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

        pydantic_model = generate_pydantic_model_from_schema(model_name)

        data = json.loads(json_only)
        print("===DATA===")
        print(data)
        pydantic_model.model_validate(data)

        # Return SimpleNamespace with attributes expected by caller
        return SimpleNamespace(
            valid=True,
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

        return SimpleNamespace(
            valid=False,
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

        # Return SimpleNamespace with attributes expected by caller
        return SimpleNamespace(
            valid=True,
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

        return SimpleNamespace(
            valid=False,
            reason=str(e),
            metadata={
                "extraneous_text_pct": extraneous_pct,
                "cleaned_json_length": 0,
                "original_length": original_length,
            },
        )