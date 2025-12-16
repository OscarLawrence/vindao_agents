"""Tests for Tool class."""

# stdlib
import inspect

# third party
# local
from vindao_agents.Tool import Tool


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
