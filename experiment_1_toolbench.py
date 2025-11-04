import json
import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Type, Union, Literal

import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from pydantic import BaseModel, create_model, ValidationError, Field, model_validator

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
TOOLBENCH_ROOT = "."

# C1: User-Only, C2: System-Schema C3 - will refer to Projects Docs!!
CONDITIONS_TO_TEST = ["C1", "C2"]

def get_llm_response(prompt: List, model_name: str) -> str:

    try:
        model = ChatOpenAI(
            model=model_name,
            temperature=0.0,
            max_tokens=1024,
        )

        messages = []
        for message_dict in prompt:
            if message_dict["role"] == "system":
                messages.append(SystemMessage(content=message_dict["content"]))
            elif message_dict["role"] == "user":
                messages.append(HumanMessage(content=message_dict["content"]))

        chat_prompt = ChatPromptTemplate.from_messages(messages)
        chain = chat_prompt | model | StrOutputParser()
        response = chain.invoke({})
        return response.strip()

    except Exception as e:
        print(f"An error occurred during LangChain API call: {e}")
        return f'{{"error": "API call failed: {str(e)}"}}'


def generate_pydantic_model_from_schema(model_name: str, schema: Dict[str, Any]) -> Type[BaseModel]:
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

class EvaluationTask(BaseModel):
    query_id: str
    query_text: str
    target_tool_name: str
    target_api_name: str
    api_schema_definition: Dict[str, Any]
    pydantic_model: Type

def load_toolbench_g_tasks(instruction_file: str, num_samples: Optional[int] = None) -> List[EvaluationTask]:
    """Loads tasks from ToolBench G1 instruction JSON and builds schema-based Pydantic models."""
    print(f"Loading tasks from {instruction_file}...")
    tasks = []
    full_path = Path(instruction_file)
    if not full_path.exists():
        print(f"ERROR: Instruction file not found at {full_path}")
        return tasks

    with open(full_path, "r", encoding="utf-8") as f:
        instruction_data = json.load(f)

    if num_samples:
        instruction_data = instruction_data[:num_samples]

    for item in tqdm(instruction_data, desc="Processing tasks"):
        try:
            query_id = str(item.get("query_id", "N/A"))
            query_text = item["query"]
            relevant_apis = item.get("relevant APIs", [])
            if not relevant_apis:
                continue

            tool_name, api_name = relevant_apis[0]
            target_schema = next(
                (api for api in item["api_list"]
                 if api["tool_name"] == tool_name and api["api_name"] == api_name),
                None
            )
            if not target_schema:
                continue

            model_name = f"{tool_name}_{api_name}_Model"
            pydantic_model = generate_pydantic_model_from_schema(model_name, target_schema)

            task = EvaluationTask(
                query_id=query_id,
                query_text=query_text,
                target_tool_name=tool_name,
                target_api_name=api_name,
                api_schema_definition=target_schema,
                pydantic_model=pydantic_model,
            )
            tasks.append(task)

        except Exception as e:
            print(f"Skipping task due to error: {e}")
            continue

    print(f"✅ Successfully loaded and processed {len(tasks)} tasks.")
    return tasks


# PROMPT BUILDER

def construct_prompt(task: EvaluationTask, condition_id: str) -> List:
    schema_str = json.dumps({
        "required_parameters": task.api_schema_definition.get("required_parameters", []),
        "optional_parameters": task.api_schema_definition.get("optional_parameters", []),
    }, indent=2)

    messages: List = []
    if condition_id == "C1":
        messages.append({
            "role": "user",
            "content": (
                f"Based on the following request, generate a JSON object with the parameters to call the correct tool.\n"
                f"Request: \"{task.query_text}\"\n\n"
                f"Your output must be a valid JSON object conforming to the following schema:\n{schema_str}\n\n"
                f"Only output the JSON object and nothing else."
            )
        })
    elif condition_id == "C2":
        messages.append({
            "role": "system",
            "content": (
                f"You are an AI assistant that extracts parameters from a user request and formats them as a JSON object.\n"
                f"You must strictly adhere to this JSON schema:\n{schema_str}"
            )
        })
        messages.append({"role": "user", "content": task.query_text})

    return messages


def safe_json_loads(s: str):
    s = re.sub(r"```(?:json)?", "", s).strip()

    def fix_newlines(match):
        return match.group(0).replace("\n", "\\n")

    s = re.sub(r'"(?:[^"\\]|\\.)*"', fix_newlines, s)
    return json.loads(s)


def validate_llm_output(output_str: str, pydantic_model: Type) -> Tuple[bool, str]:

    try:
        json_block = safe_json_loads(output_str)
    except json.JSONDecodeError as e:
        return False, f"Error: Malformed JSON (JSONDecodeError: {str(e)})"
    except Exception as e:
        return False, f"Error: Unexpected error while extracting/parsing JSON ({str(e)})"

    try:
        pydantic_model.model_validate(json_block)
        return True, "Success"
    except ValidationError as e:
        first = e.errors()[0] if e.errors() else {}
        loc = ".".join(map(str, first.get("loc", [])))
        msg = first.get("msg", "validation error")
        return False, f"Error: Pydantic Validation ({loc}: {msg})"
    except Exception as e:
        return False, f"Error: Unknown validation error ({str(e)})"


# MAIN

if __name__ == "__main__":
    # How to run the model.
    INSTRUCTION_FILE_PATH = "datasets/toolbenc_test_instruction/G1_instruction.json"

    NUM_SAMPLES = 100
    tasks = load_toolbench_g_tasks(INSTRUCTION_FILE_PATH, num_samples=NUM_SAMPLES)

    # Sample pipeline test with model.
    prompt = construct_prompt(tasks[1], "C1")
    llm_output = get_llm_response(prompt, "gpt-4o-mini-2024-07-18")
    print("LLM Output:\n", llm_output)

    is_valid, reason = validate_llm_output(llm_output, tasks[1].pydantic_model)
    print("Validation Result:", is_valid, reason)
