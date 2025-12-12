import json
import re
from types import SimpleNamespace
from typing import Any, Dict, List, Literal, Optional, Tuple, Type, Union

import jsonschema
from pydantic import BaseModel, Field, ValidationError, create_model

from experiments.validators.base_validator import ValidatorOutput


class SSTResponse(BaseModel):
    label: Literal["positive", "negative"]


class QQPResponse(BaseModel):
    label: Literal["equivalent", "not_equivalent"]


class QNLIResponse(BaseModel):
    label: Literal["true", "false"]


class MNLIResponse(BaseModel):
    label: Literal["entailment", "neutral", "contradiction"]


class RTEResponse(BaseModel):
    label: Literal["entailment", "not_entailment"]


RESPONSE_TYPES: dict[str, BaseModel] = {
    "SST": SSTResponse,
    "QQP": QQPResponse,
    "QNLI": QNLIResponse,
    "MNLI": MNLIResponse,
    "RTE": RTEResponse,
}

LABEL_TRANSLATIONS = {
    "SST": {"positive": 1, "negative": 0},
    "QQP": {"equivalent": 1, "not_equivalent": 0},
    "QNLI": {"true": 0, "false": 1},
    "MNLI": {"entailment": 0, "neutral": 1, "contradiction": 2},
    "RTE": {"entailment": 0, "not_entailment": 1},
}


def validate_glue(
    output: Any, task: Literal["SST", "QQP", "QNLI", "MNLI", "RTE"], label: int
) -> ValidatorOutput:
    try:
        model = RESPONSE_TYPES[task]
        parsed = model.model_validate_json(output)
        predicted_label = LABEL_TRANSLATIONS[task][parsed.label]
        is_correct = predicted_label == label
        return ValidatorOutput(
            is_valid=is_correct,
            reason=(
                f"predicted: {predicted_label}, expected: {label}"
                if not is_correct
                else ""
            ),
            metadata={"task": task, "predicted": predicted_label, "expected": label},
        )
    except ValidationError as ve:
        return ValidatorOutput(
            is_valid=False,
            reason=f"validation error: {ve}",
            metadata={"task": task, "predicted": None, "expected": label},
        )
