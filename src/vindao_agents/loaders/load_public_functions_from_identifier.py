"""Loader for public functions from a module identifier."""

# stdlib
from collections.abc import Callable


def load_public_functions_from_identifier(identifier: str) -> list[tuple[str, Callable]]:
    """Load public functions from a given module identifier."""
    import importlib
    import inspect
    try:
        module = importlib.import_module(identifier)
    except ModuleNotFoundError:
        module = importlib.import_module("vindao_agents." + identifier)
    loaded = []
    for name, obj in inspect.getmembers(module):
        if name.startswith('_'):
            continue
        if name.startswith('test_'):
            continue
        if inspect.isfunction(obj):
            loaded.append((name, obj))
    return loaded
