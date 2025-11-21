# usage: main.py <config_path>

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from retry import retry
from tqdm import tqdm

from experiments.builders.builders import Message, get_builders
from experiments.dataloader.loaders import get_loader
from experiments.models.models import BaseClient, get_client
from experiments.validators.base_validator import ValidatorOutput
from experiments.validators.validators import get_validator

load_dotenv()


@retry(TimeoutError, tries=3, delay=10, backoff=3, logger=None)
def call_model_with_retry(client: BaseClient, messages: list[Message]) -> str:
    try:
        return client.chat(messages)
    except Exception as e:
        if "429" in str(e):
            # retry if rate limit hit
            print(f"\n  ⚠️ Rate limit hit! Retrying in a few seconds...")
            raise TimeoutError()
        raise e


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
        print("Saving outputs to:", output_dir)

        with output_dir.open("w") as f:
            f.write("model,builder,input,output,valid,reason,metadata\n")

            for model in self.models:
                client = get_client(model)
                for builder_name, builder in self.builders.items():
                    for data in tqdm(
                        self.data_loader,
                        desc=f"{model:<22} {builder_name:<38}",
                        unit="sample",
                    ):
                        messages = builder(*(data[col] for col in self.builder_inputs))
                        output = call_model_with_retry(client, messages)

                        valid: ValidatorOutput = self.validator(
                            output, *(data[col] for col in self.validator_inputs)
                        )

                        print("===Validator===")
                        print(valid)
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


if __name__ == "__main__":
    assert len(sys.argv) == 2, "Usage: python main.py <config_path>"

    pipeline = ExperimentPipeline(sys.argv[1])
    print(f"Starting experiment using config: {sys.argv[1]}")

    pipeline.run()
