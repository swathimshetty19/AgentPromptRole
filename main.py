# usage: main.py <config_path>

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from tqdm import tqdm

from experiments.builders.builders import Message, get_builders
from experiments.dataloader.loaders import get_loader
from experiments.models.models import BaseClient, get_client
from experiments.validators.base_validator import ValidatorOutput
from experiments.validators.validators import get_validator

load_dotenv()


def call_model_with_retry(client: BaseClient, messages: list[Message]) -> str:
    """
    Call model with retry only for rate limits, not for content filtering
    """
    tries = 3
    delay = 10
    backoff = 3
    
    for attempt in range(tries):
        try:
            return client.chat(messages)
        except Exception as e:
            error_str = str(e)
            
            # Check for content filtering error - don't retry, return None
            if "data_inspection_failed" in error_str or "inappropriate content" in error_str:
                print(f"\n  ⚠️ Content filtered by API, skipping this sample...")
                return None  # Return None to indicate content was filtered
            
            # Check for rate limit - retry
            if "429" in error_str:
                if attempt < tries - 1:  # Don't sleep on last attempt
                    print(f"\n  ⚠️ Rate limit hit! Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= backoff
                    continue
                else:
                    raise e
            
            # For other errors, raise immediately
            raise e
    
    # Should not reach here, but just in case
    raise Exception("Max retries reached")


class ExperimentPipeline:
    def __init__(self, config_path: str):
        with Path(config_path).open() as f:
            self._cfg = yaml.safe_load(f)

        assert self._cfg.get("config_version") == 1.0, "Unsupported config version"
        self.experiment_name: str = self._cfg["experiment_name"]
        self.models: list[str] = self._cfg["models"]

        dataset_cfg: dict[str, Any] = self._cfg["dataset"]
        self.data_loader = get_loader(
            dataset_cfg["loader"], dataset_cfg["path"], dataset_cfg.get("limit", -1)
        )
        self.builder_inputs: list[str] = dataset_cfg.get("builder_inputs", [])
        self.validator_inputs: list[str] = dataset_cfg.get("validator_inputs", [])

        self.builders = get_builders(self._cfg["builders"])
        self.validator = get_validator(self._cfg["validator"])

    def run(self) -> None:
        experiment_name = (
            self.experiment_name + "_" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        )
        output_dir = Path("outputs") / (experiment_name + ".csv")
        output_dir.parent.mkdir(exist_ok=True)
        print("Saving outputs to:", output_dir)
        
        # Track statistics
        skipped_count = 0
        processed_count = 0

        with output_dir.open("w") as f:
            f.write("model,builder,input,output,valid,reason,metadata\n")

            for model in self.models:
                client = get_client(model)
                for builder_name, builder in self.builders.items():
                    pbar = tqdm(
                        self.data_loader,
                        desc=f"{model:<22} {builder_name:<38}",
                        unit="sample",
                    )
                    
                    for data in pbar:
                        try:
                            messages = builder(*(data[col] for col in self.builder_inputs))
                            output = call_model_with_retry(client, messages)
                            
                            # Check if content was filtered
                            if output is None:
                                skipped_count += 1
                                # Write a row indicating this was skipped
                                f.write(
                                    (
                                        f"{model},"
                                        f"{builder_name},"
                                        f"\"{json.dumps(messages).replace('\"', '\"\"')}\","
                                        f"\"[CONTENT_FILTERED]\","
                                        f"False,"
                                        f"\"Content filtered by API\","
                                        f"\"{json.dumps({'content_filtered': True})}\"\n"
                                    )
                                )
                                f.flush()
                                # Update progress bar with skip count
                                pbar.set_postfix({"skipped": skipped_count})
                                continue
                            
                            valid: ValidatorOutput = self.validator(
                                output, *(data[col] for col in self.validator_inputs)
                            )

                            print("===Validator===")
                            print(valid)
                            
                            processed_count += 1
                            f.write(
                                (
                                    f"{model},"
                                    f"{builder_name},"
                                    f"\"{json.dumps(messages).replace('\"', '\"\"')}\","
                                    f"\"{output.replace('\"', '\"\"')}\","
                                    f"{valid.valid},"
                                    f"\"{valid.reason.replace('\"', '\"\"')}\","
                                    f"\"{json.dumps(valid.metadata).replace('\"', '\"\"')}\"\n"
                                )
                            )
                            f.flush()
                            
                        except Exception as e:
                            print(f"\n  ❌ Error processing sample: {e}")
                            # Log error and continue
                            f.write(
                                (
                                    f"{model},"
                                    f"{builder_name},"
                                    f"\"ERROR\","
                                    f"\"ERROR: {str(e).replace('\"', '\"\"')}\","
                                    f"False,"
                                    f"\"Processing error\","
                                    f"\"{json.dumps({'error': True})}\"\n"
                                )
                            )
                            f.flush()
                            continue
        
        print(f"\n✅ Experiment complete!")
        print(f"   Processed: {processed_count} samples")
        print(f"   Skipped (content filtered): {skipped_count} samples")
        print(f"   Output saved to: {output_dir}")


if __name__ == "__main__":
    assert len(sys.argv) == 2, "Usage: python main.py <config_path>"

    pipeline = ExperimentPipeline(sys.argv[1])
    print(f"Starting experiment using config: {sys.argv[1]}")

    pipeline.run()