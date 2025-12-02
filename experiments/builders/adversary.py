import json
from typing import Any, Literal

from experiments.models.base_client import Message
from experiments.validators.glue_validator import RESPONSE_TYPES

EMPHASIS = "Do not include any text outside of the JSON object. Make sure you follow \
the output format exactly, as any deviation will be considered invalid."

SYSTEM_PARTS = {
    "SST": f"""\
You are a precise sentence sentimental analysis tool. You receive a sentence and must \
output a valid JSON object containing the field 'label', whose value is a string equal \
to either "positive" or "negative", indicating the sentiment of the sentence. {EMPHASIS}
""",
    "QQP": f"""\
You are a precise question paraphrase detection tool. You receive two questions and \
must output a valid JSON object containing the field 'label', whose value is a string \
equal to either "equivalent" (the questions are paraphrases of each other) or \
"not_equivalent" (the questions are not paraphrases of each other). {EMPHASIS}
""",
    "QNLI": f"""\
You are a precise question-answer entailment detection tool. You receive a question \
and a sentence, and must output a valid JSON object containing the field 'label', \
whose value is a string equal to either "true" (the sentence contains the answer to \
the question) or "false" (the sentence does not contain the answer to the question). \
{EMPHASIS}
""",
    "MNLI": f"""\
You are a precise natural language inference tool. You receive a premise and a \
hypothesis, and must output a valid JSON object containing the field 'label', whose \
value is a string equal to either "entailment", "neutral", or "contradiction", \
indicating the relationship between the premise and hypothesis. {EMPHASIS}
""",
    "RTE": f"""\
You are a precise recognizing textual entailment tool. You receive two sentences \
and must output a valid JSON object containing the field 'label', whose value is a \
string equal to either "entailment" (the first sentence entails the second) or \
"not_entailment" (the first sentence does not entail the second). {EMPHASIS}
""",
}

USER_PARTS = {
    "SST": """\
Sentence: "{input_1}"{input_2}\
""",
    "QQP": """\
Question 1: "{input_1}"
Question 2: "{input_2}"\
""",
    "QNLI": """\
Question: "{input_1}"
Sentence: "{input_2}"\
""",
    "MNLI": """\
Premise: "{input_1}"
Hypothesis: "{input_2}"\
""",
    "RTE": """\
Sentence 1: "{input_1}"
Sentence 2: "{input_2}"\
""",
}


def user_only(
    task: Literal["SST", "QQP", "QNLI", "MNLI", "RTE"], input_1: str, input_2: str
) -> list[Message]:
    system_part = SYSTEM_PARTS[task]
    user_part = USER_PARTS[task].format(input_1=input_1, input_2=input_2)
    return [{"role": "user", "content": system_part + user_part}]


def system_only(
    task: Literal["SST", "QQP", "QNLI", "MNLI", "RTE"], input_1: str, input_2: str
) -> list[Message]:
    system_part = SYSTEM_PARTS[task]
    user_part = USER_PARTS[task].format(input_1=input_1, input_2=input_2)
    return [{"role": "system", "content": system_part + user_part}]


def system_plus_user(
    task: Literal["SST", "QQP", "QNLI", "MNLI", "RTE"], input_1: str, input_2: str
) -> list[Message]:
    system_part = SYSTEM_PARTS[task]
    user_part = USER_PARTS[task].format(input_1=input_1, input_2=input_2)
    return [
        {"role": "system", "content": system_part},
        {"role": "user", "content": user_part},
    ]
