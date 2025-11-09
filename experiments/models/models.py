from experiments.models.base_client import BaseClient
from experiments.models.openai_compat import OpenAICompatClient


def get_client(model_name: str) -> BaseClient:
    """Returns a client instance for a given model name."""
    if model_name.startswith("openai"):
        return OpenAICompatClient(model_name)
    raise ValueError(f"Unsupported model: {model_name}")
