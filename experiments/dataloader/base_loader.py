from abc import ABC, abstractmethod
from typing import Any


class BaseLoader(ABC):
    @abstractmethod
    def __init__(self, data_path: str, limit: int) -> None:
        pass

    @abstractmethod
    def __len__(self) -> int:
        """Returns the total length of the dataset."""
        pass

    @abstractmethod
    def __next__(self) -> dict[str, Any]:
        """Returns the next data sample from the dataset."""
        pass

    def __iter__(self):
        return self
