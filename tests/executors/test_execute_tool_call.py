"""Tests for executor functions."""

# third party
import pytest

# local
from vindao_agents.Tool import Tool
from vindao_agents.executors.execute_tool_call import execute_tool_call


class TestExecuteToolCall:

    def test_execute_tool_call_success(self):
        def sample_tool_1(x, y):
            return x + y

        tool = Tool(sample_tool_1)
        tool_call = "sample_tool_1(2, 3)"
        result = execute_tool_call(tool_call, tool)
        assert result == 5

    def test_execute_tool_call_exception(self):
        def faulty_tool(x):
            return 10 / x

        tool = Tool(faulty_tool)
        tool_call = "faulty_tool(0)"
        result = execute_tool_call(tool_call, tool)
        assert "division by zero" in result
