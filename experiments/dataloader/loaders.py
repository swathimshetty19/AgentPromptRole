from experiments.dataloader.adherence import JsonSchemaLoader
from experiments.dataloader.adversarial_glue import AdversarialGlueLoader
from experiments.dataloader.base_loader import BaseLoader


def get_loader(loader_name: str, data_path: str, limit: int) -> BaseLoader:
    """Returns the requested Data Loader."""
    # NOTE: add new loaders here
    if loader_name == "json_schema":
        return JsonSchemaLoader(data_path, limit)
    if loader_name == "adversarial_glue":
        return AdversarialGlueLoader(data_path, limit)

    raise ValueError(f"Loader '{loader_name}' not recognized.")
