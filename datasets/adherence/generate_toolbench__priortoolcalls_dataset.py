import json
import random
from pathlib import Path
from typing import Optional

from tqdm import tqdm

TOOLBENCH_ROOT = "."


def load_toolbench_g_tasks(
    instruction_files: list[str],
    dataset_name: str,
    num_samples: Optional[int] = None,
    done_probability: float = 0.5,
    seed: Optional[int] = None,
) -> None:
    """
    Loads tasks from instruction JSONs and builds a JSONL dataset, injecting random prior_tool_calls.

    Behavior:
    - For each sample we collect the set of distinct tool names from item["api_list"].
    - With probability `done_probability` we include ALL relevant tools in prior_tool_calls
      and set target_api_name to "done" (meaning no further tool required).
    - Otherwise we include ALL relevant tools EXCEPT the target tool, so the expected next
      tool remains the target tool (api_name).
    - If there is only one relevant tool we skip the 'except' case and just mark done.

    Args:
      instruction_files: list of filenames inside toolbenc_test_instruction directory
      dataset_name: output base filename (written to f"{dataset_name}.jsonl")
      num_samples: optional max number of samples to load
      done_probability: probability to mark a sample as already-complete (expected="done")
      seed: optional random seed for reproducibility
    """
    if seed is not None:
        random.seed(seed)

    dataset_dir = Path(__file__).parent / "toolbenc_test_instruction"
    tasks = []

    for filename in instruction_files:
        filepath = dataset_dir / filename
        if not filepath.exists() or not filepath.is_file():
            print(f"❌ {filepath} not found, skipping")
            continue

        with filepath.open("r", encoding="utf-8") as f:
            try:
                instruction_data = json.load(f)
            except Exception as e:
                print(f"Skipping {filename} due to JSON load error: {e}")
                continue

        for item in tqdm(instruction_data, desc=f"Processing {filename}"):
            if num_samples is not None and len(tasks) >= num_samples:
                break

            try:
                query_id = str(item.get("query_id", "N/A"))
                query_text = item.get("query") or item.get("query_text") or ""
                relevant_apis = item.get("relevant APIs", []) or item.get("relevant_apis", [])
                # fallback: if item contains api_list, extract tool_name+api_name pairs
                if not relevant_apis and isinstance(item.get("api_list"), list):
                    # Some toolbench formats provide api_list entries like {"tool_name": "...", "api_name": "...", ...}
                    relevant_apis = []
                    for api in item.get("api_list", []):
                        tn = api.get("tool_name")
                        an = api.get("api_name")
                        if tn and an:
                            relevant_apis.append([tn, an])

                if not relevant_apis:
                    # nothing to do; skip sample
                    continue

                # target pair (pick first relevant pair in the list if present)
                tool_name, api_name = relevant_apis[0]

                # find matching schema in api_list (same as original code)
                target_schema = next(
                    (
                        api
                        for api in item.get("api_list", [])
                        if api.get("tool_name") == tool_name
                        and api.get("api_name") == api_name
                        and api.get("optional_parameters") is not None
                        and api.get("required_parameters") is not None
                    ),
                    None,
                )
                if not target_schema:
                    continue

                model_name = f"{tool_name}_{api_name}_Model"

                # Build a set of distinct relevant tool names for this item.
                # Use relevant_apis entries and fallback to api_list tool names.
                tool_names_set = []
                for pair in relevant_apis:
                    if isinstance(pair, (list, tuple)) and len(pair) >= 1:
                        tn = pair[0]
                        if tn and tn not in tool_names_set:
                            tool_names_set.append(tn)
                # also include any tool_name found in api_list
                for api in item.get("api_list", []):
                    tn = api.get("tool_name")
                    if tn and tn not in tool_names_set:
                        tool_names_set.append(tn)

                # If we still have no tool names, skip
                if not tool_names_set:
                    continue

                # Decide whether this sample should be 'done' (all tools already called)
                # or missing exactly the target tool (expected = target api_name).
                # If only one tool exists, prefer done.
                if len(tool_names_set) == 1:
                    make_done = True
                else:
                    make_done = random.random() < done_probability

                if make_done:
                    prior_calls = list(tool_names_set)  # all tools called
                    expected_target = "done"
                else:
                    # include all but the target tool_name (so the expected next tool remains target)
                    # ensure the target tool_name is present in the set; if not, fallback to removing a random tool
                    if tool_name in tool_names_set:
                        prior_calls = [t for t in tool_names_set if t != tool_name]
                    else:
                        # remove one random tool to simulate missing-one scenario
                        remove_t = random.choice(tool_names_set)
                        prior_calls = [t for t in tool_names_set if t != remove_t]
                    expected_target = api_name  # expected is the api_name (unchanged)

                # Make a deep-ish copy of the target_schema to avoid mutating original structures
                schema_copy = dict(target_schema)
                # Inject prior_tool_calls into the schema (builder expects it here)
                schema_copy["prior_tool_calls"] = prior_calls

                tasks.append(
                    {
                        "query_text": query_text,
                        "query_id": query_id,
                        "target_api_name": expected_target,
                        "api_schema_definition": schema_copy,
                        "model_name": model_name,
                    }
                )
            except Exception as e:
                print(f"Skipping task due to error: {e}")
                continue

    print(f"✅ Successfully loaded and processed {len(tasks)} tasks.")

    output_file = f"{dataset_name}.jsonl"
    with open(output_file, "w", encoding="utf-8") as f:
        for sample in tasks:
            f.write(json.dumps(sample) + "\n")


# Example usage
if __name__ == "__main__":
    load_toolbench_g_tasks(
        [
            "G1_tool.json",
            "G1_category.json",
            "G2_category.json",
            "G1_instruction.json",
            "G2_instruction.json",
            "G3_instruction.json",
        ],
        "toolbench_tool_with_prior",
        num_samples=500,
        done_probability=0.5,
        seed=42,
    )
