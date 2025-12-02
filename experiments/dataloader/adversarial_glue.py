import json
from pathlib import Path
from typing import Any

from experiments.dataloader.base_loader import BaseLoader


class AdversarialGlueLoader(BaseLoader):
    def __init__(self, data_path: str, limit: int) -> None:
        data_path = Path(data_path)
        if not data_path.exists() or not data_path.is_file():
            raise FileNotFoundError(f"Data file not found: {data_path}")

        self.tasks = {
            "sst2": ("SST", "sentence", None),
            "qqp": ("QQP", "question1", "question2"),
            "mnli": ("MNLI", "premise", "hypothesis"),
            "mnli-mm": ("MNLI", "premise", "hypothesis"),
            "qnli": ("QNLI", "question", "sentence"),
            "rte": ("RTE", "sentence1", "sentence2"),
        }
        self._data: list[dict[str, Any]] = []

        self.data_path = data_path
        with data_path.open("r") as f:
            data: dict[str, list[dict[str, Any]]] = json.load(f)
            for task, (taskname, inp1, inp2) in self.tasks.items():
                for item in data[task]:
                    datum = {
                        "task": taskname,
                        "input_1": item[inp1],
                        "input_2": item[inp2] if inp2 is not None else "",
                        "label": item["label"],
                    }
                    self._data.append(datum)

        self._index = 0
        self.limit = limit if limit >= 0 else len(self._data)

    def __len__(self) -> int:
        """Returns the total length of the dataset."""
        return min(len(self._data), self.limit)

    def __next__(self) -> dict[str, Any]:
        """Returns the next data sample from the dataset."""
        if self._index >= min(len(self._data), self.limit):
            raise StopIteration

        datum = self._data[self._index]
        self._index += 1

        return datum

    def __iter__(self):
        self._index = 0
        return self
