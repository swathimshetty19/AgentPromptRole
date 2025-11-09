from abc import ABC, abstractmethod

from typing_extensions import TypedDict


class Message(TypedDict):
    role: str
    content: str


class BaseClient(ABC):
    @abstractmethod
    def __init__(self, model: str) -> None:
        """Initializes the client with the specified model name."""
        pass

    @abstractmethod
    def chat(self, messages: list[Message]) -> str:
        """Sends a completion request to the model and return its output as a string."""
        pass
