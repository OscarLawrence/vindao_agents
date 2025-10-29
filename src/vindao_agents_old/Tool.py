"""Function wrapper providing metadata extraction and signature analysis for dynamic tool registration."""
# stdlib
import inspect
from typing import Callable

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
        argsspec = inspect.getfullargspec(func)
        self.parameters = {arg: argsspec.annotations.get(arg, None) for arg in argsspec.args}
        self.arguments = [(arg, self.parameters[arg]) for arg in argsspec.args]
        self.return_type = argsspec.annotations.get('return', 'unknown')
        

    def __call__(self, *args, **kwargs) -> str:
        """Invoke the wrapped function with the extracted parameters."""
        try:
            return str(self.func(*args, **kwargs))
        except Exception as e:
            return format_exception(e)


    def __str__(self) -> str:
        return f"Tool(name={self.name}, description={self.description}, signature={self.signature})"