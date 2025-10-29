"""Execute a tool call string using the provided tool."""

# local
from vindao_agents.Tool import Tool
from vindao_agents.formatters import format_exception

def execute_tool_call(tool_call: str, tool: Tool) -> str:
    try:
        return eval(tool_call, {tool.name: tool.func})
    except Exception as e:
        return format_exception(e)
    

class TestExecuteToolCall:
    
    def test_execute_tool_call_success(self):
        def sample_tool(x, y):
            return x + y
        
        tool = Tool(sample_tool)
        tool_call = "sample_tool(2, 3)"
        result = execute_tool_call(tool_call, tool)
        assert result == 5

    def test_execute_tool_call_exception(self):
        def faulty_tool(x):
            return 10 / x
        
        tool = Tool(faulty_tool)
        tool_call = "faulty_tool(0)"
        result = execute_tool_call(tool_call, tool)
        assert "division by zero" in result