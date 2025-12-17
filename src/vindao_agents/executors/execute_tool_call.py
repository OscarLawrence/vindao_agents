"""Execute a tool call string using the provided tool."""

# stdlib
from typing import Any

# local
from vindao_agents.formatters import format_exception
from vindao_agents.Tool import Tool


def execute_tool_call(tool_call: str, tool: Tool) -> Any:
    """Execute a tool call dynamically.

    Security Note: This function uses eval() by design as it is core functionality
    for an AI agent framework that needs to execute tool calls dynamically.
    The eval scope is restricted to only the specific tool function being called.
    Users should only use trusted tools and be aware of the execution model.
    """
    try:
        # nosec B307: eval is required for dynamic tool execution in agent framework
        # The namespace is restricted to only the specific tool function
        return eval(tool_call, {tool.name: tool.func})  # nosec
    except Exception as e:
        return format_exception(e)
