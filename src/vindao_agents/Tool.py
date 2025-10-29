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

    def to_instruction(self, include_source: bool = False) -> str:
        """Generate a string representation of the tool for inclusion in prompts or documentation."""
        if include_source:
            return self.source + '\n\n'
        else:
            return f"def {self.name}{self.signature}\n\t\"\"\"{self.description}\"\"\"\n\n"
        
    def __call__(self, *args, **kwargs) -> str:
        """Invoke the wrapped function with the extracted parameters."""
        try:
            return str(self.func(*args, **kwargs))
        except Exception as e:
            return format_exception(e)

class TestTool:
    def test_tool_metadata_extraction(self):
        def sample_tool(x: int, y: int) -> int:
            """Adds two integers."""
            return x + y

        tool = Tool(sample_tool)

        assert tool.name == "sample_tool"
        assert tool.description == "Adds two integers."
        assert tool.source == inspect.getsource(sample_tool)
        assert tool.signature == inspect.signature(sample_tool)

    def test_tool_invocation_success(self):
        def sample_tool(x: int, y: int) -> int:
            return x + y

        tool = Tool(sample_tool)
        result = tool(2, 3)
        assert result == "5"

    def test_tool_invocation_exception(self):
        def faulty_tool(x: int, y: int) -> int:
            return x / y  # Potential division by zero

        tool = Tool(faulty_tool)
        result = tool(2, 0)
        assert "ZeroDivisionError" in result