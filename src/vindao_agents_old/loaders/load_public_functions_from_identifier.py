# standard library imports
from typing import Callable


def load_public_functions_from_identifier(identifier: str) -> list[tuple[str, Callable]]:
    """Load public functions from a given module identifier."""
    import importlib
    import inspect
    module = importlib.import_module(identifier)
    loaded = []
    for name, obj in inspect.getmembers(module):
        if name.startswith('_'):
            continue
        if inspect.isfunction(obj):
            loaded.append((name, obj))
    return loaded