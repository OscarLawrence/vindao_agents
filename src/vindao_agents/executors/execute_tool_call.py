"""Execute a tool call string using the provided tool."""

# stdlib
from typing import Any

# local
from vindao_agents.formatters import format_exception
from vindao_agents.Tool import Tool


def execute_tool_call(tool_call: str, tool: Tool) -> Any:
    try:
        return eval(tool_call, {tool.name: tool.func})
    except Exception as e:
        return format_exception(e)
