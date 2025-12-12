from experiments.models.base_client import BaseClient
from experiments.models.chatopenai_compat import ChatOpenAICompatClient
from experiments.models.openai_compat import OpenAICompatClient
from experiments.models.qwen_compat import QwenCompatClient


def get_client(model_name: str) -> BaseClient:
    """Returns a client instance for a given model name."""
    # NOTE: add new model clients here
    if model_name.startswith("openai"):
        return OpenAICompatClient(model_name)
    if model_name.startswith("qwen"):
        return QwenCompatClient(model_name)
    if model_name.startswith("chatopenai"):
        return ChatOpenAICompatClient(model_name)

    raise ValueError(f"Unsupported model: {model_name}")
