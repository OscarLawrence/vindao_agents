# Standard library imports
import re
import ast

# Third-party imports
from uuid import uuid4 as uuid

# Local imports
from vindao_agents.formatters import format_exception
from vindao_agents.Tool import Tool
from vindao_agents.models.tool import ToolCall

def parse_and_execute_tool_call(content: str, tools: dict[str, Tool]) -> ToolCall | None:
    """Parse a tool call from the given content.
    Example tool call: @tool_name(arg1, arg2, key=value)

    Supports all Python literals: strings, numbers, lists, dicts, tuples, sets, booleans, None
    Examples:
        @readFile('test.py')
        @writeFile('data.json', {'key': 'value'})
        @processList([1, 2, 3], options={'verbose': True})
    """
    if not '@' in content or not '(' in content or not ')' in content:
        return None
    pattern = r"@(" + "|".join(re.escape(name) for name in tools) + r")\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)"
    match = re.search(pattern, content)
    if not match:
        return None
    tool_name = match.group(1)
    call = match.group(0)[1:]  # Remove the '@' symbol
    tree = ast.parse(call, mode='eval')
    parameters = {}
    call_id = uuid().hex
    try:
        # Parse positional arguments using ast.literal_eval for safety
        for arg in tree.body.args:
            arg_str = ast.unparse(arg)
            value = ast.literal_eval(arg_str)
            param_name = tools[tool_name].arguments[len(parameters)][0]
            parameters[param_name] = value

        # Parse keyword arguments using ast.literal_eval for safety
        for keyword in tree.body.keywords:
            value_str = ast.unparse(keyword.value)
            value = ast.literal_eval(value_str)
            parameters[keyword.arg] = value
        result = tools[tool_name](**parameters)
        return ToolCall(
            name=tool_name,
            call=call,
            id=call_id,
            parameters=parameters,
            result=result
        )
    except Exception as e:
        return ToolCall(
            name=tool_name,
            call=call,
            id=call_id,
            parameters={},
            result=format_exception(e)
        )

