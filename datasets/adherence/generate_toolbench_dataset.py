import json
from pathlib import Path
from typing import Optional

from tqdm import tqdm

TOOLBENCH_ROOT = "."


def load_toolbench_g_tasks(
    instruction_files: list[str],
    dataset_name: str,
    num_samples: Optional[int] = None,
) -> None:
    """Loads tasks from instruction JSONs and builds schema-based Pydantic models."""
    dataset_dir = Path(__file__).parent / "toolbenc_test_instruction"
    tasks = []

    for filename in instruction_files:
        filepath = dataset_dir / filename
        if not filepath.exists() or not filepath.is_file():
            print(f"❌ {filepath} not found, skipping")
            continue

        with filepath.open("r", encoding="utf-8") as f:
            instruction_data = json.load(f)

        for item in tqdm(instruction_data, desc=f"Processing {filename}"):
            if len(tasks) == num_samples:
                break

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


# Generate Toolbench Dataset
load_toolbench_g_tasks(
    [
        "G1_tool.json",
        "G1_category.json",
        "G2_category.json",
        "G1_instruction.json",
        "G2_instruction.json",
        "G3_instruction.json",
    ],
    "toolbench_tool",
    500,
)
