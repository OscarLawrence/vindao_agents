"""Function wrapper providing metadata extraction and signature analysis for dynamic tool registration."""

# stdlib
import inspect
from collections.abc import Callable

# local
from vindao_agents.formatters.format_exception import format_exception


class Tool:
    """Function wrapper extracting metadata and parameters for dynamic tool registration and execution."""

    def __init__(self, func: Callable) -> None:
        self.name = func.__name__
        self.description = inspect.getdoc(func)
        self.source = inspect.getsource(func)
        self.signature = inspect.signature(func)
        self.func = func

    def to_instruction(self, include_source: bool = False) -> str:
        """Generate a string representation of the tool for inclusion in prompts or documentation."""
        if include_source:
            return self.source + "\n\n"
        else:
            return f'def {self.name}{self.signature}\n\t"""{self.description}"""\n\n'

    def __call__(self, *args, **kwargs) -> str:
        """Invoke the wrapped function with the extracted parameters."""
        try:
            return str(self.func(*args, **kwargs))
        except Exception as e:
            return format_exception(e)
