"""Loader for public functions from a module identifier."""

# stdlib
from typing import Callable


def load_public_functions_from_identifier(identifier: str) -> list[tuple[str, Callable]]:
    """Load public functions from a given module identifier."""
    import importlib
    import inspect
    try:
        module = importlib.import_module(identifier)
    except ModuleNotFoundError as e:
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

class TestLoadPublicFunctions:
    def test_load_functions(self):
        # Assuming there's a module named 'sample_module' with public functions
        functions = load_public_functions_from_identifier('vindao_agents.formatters.format_exception')
        function_names = [name for name, _ in functions]
        assert 'format_exception' in function_names
        assert not 'TestFormatException' in function_names
        assert len(functions) == 1  # Only one public function expected

    
