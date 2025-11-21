import json
from pathlib import Path
from typing import Optional

from tqdm import tqdm

TOOLBENCH_ROOT = "."


def load_toolbench_g_tasks(
    instruction_file: str, dataset_name: str, num_samples: Optional[int] = None
):
    """Loads tasks from ToolBench G1 instruction JSON and builds schema-based Pydantic models."""
    print(f"Loading tasks from {instruction_file}...")
    tasks = []
    full_path = Path(instruction_file)
    print(full_path.resolve())
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
                (
                    api
                    for api in item["api_list"]
                    if api["tool_name"] == tool_name
                    and api["api_name"] == api_name
                    and api["optional_parameters"]
                    and api["required_parameters"]
                ),
                None,
            )
            if not target_schema:
                continue

            model_name = f"{tool_name}_{api_name}_Model"

            # task = EvaluationTask(
            #     query_id=query_id,
            #     query_text=query_text,
            #     target_tool_name=tool_name,
            #     target_api_name=api_name,
            #     api_schema_definition=target_schema,
            #     pydantic_model=pydantic_model,
            # )
            tasks.append(
                {
                    "query_text": query_text,
                    "query_id": query_id,
                    "target_api_name": api_name,
                    "api_schema_definition": target_schema,
                    "model_name": model_name,
                }
            )

        except Exception as e:
            print(f"Skipping task due to error: {e}")
            continue

    print(f"✅ Successfully loaded and processed {len(tasks)} tasks.")

    output_file = f"{dataset_name}.jsonl"
    with open(output_file, "w") as f:
        for sample in tasks:
            f.write(json.dumps(sample) + "\n")

    # return tasks


# Generate Toolbench Dataset
load_toolbench_g_tasks(
    "datasets/adherence/toolbenc_test_instruction/G3_instruction.json", "toolbench_instruction3", 500
)
