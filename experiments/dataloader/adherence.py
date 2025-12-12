import json
from pathlib import Path
from typing import Any

from experiments.dataloader.base_loader import BaseLoader


class JsonSchemaLoader(BaseLoader):
    def __init__(self, data_path: str, limit: int) -> None:
        data_path = Path(data_path)
        if not data_path.exists() or not data_path.is_file():
            raise FileNotFoundError(f"Data file not found: {data_path}")

        self.data_path = data_path
        with data_path.open("r") as f:
            self._data = [line.strip() for line in f if line.strip()]

        self._index = 0
        self.limit = limit if limit >= 0 else len(self._data)

    def __len__(self) -> int:
        """Returns the total length of the dataset."""
        return min(len(self._data), self.limit)

    def __next__(self) -> dict[str, Any]:
        """Returns the next data sample from the dataset."""
        if self._index >= min(len(self._data), self.limit):
            raise StopIteration

        line = self._data[self._index]
        self._index += 1

        return json.loads(line)

    def __iter__(self):
        self._index = 0
        return self
