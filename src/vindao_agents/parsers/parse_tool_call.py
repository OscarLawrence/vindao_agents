"""Parser for tool calls in the format @{tool_name}(...)"""
# stdlib
import re

def parse_tool_call(content: str, tool_names: list[str]) -> tuple[str, str] | None:
    # pattern to match @{tool_name}(...) where tool_name is in tool_names
    pattern = r"@(" + "|".join(re.escape(name) for name in tool_names) + r")\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)"
    match = re.search(pattern, content)
    
    if match:
        return match.group(1), match.group(0)[1:]  # Remove the '@' symbol
    return None

class TestParseToolCall:

    def test_no_tool_call(self):
        content = "This is a test without tool call."
        tool_names = ["tool1", "tool2"]
        result = parse_tool_call(content, tool_names)
        assert result is None

    def test_incomplete_tool_call(self):
        content = "@tool1(arg1, arg2"
        tool_names = ["tool1", "tool2"]
        result = parse_tool_call(content, tool_names)
        assert result is None
    
    def test_simple_tool_call(self):
        content = "@tool1('value1', param2=42)"
        tool_names = ["tool1", "tool2"]
        result = parse_tool_call(content, tool_names)
        assert result[0] == "tool1"
        assert result[1] == "tool1('value1', param2=42)"
    
    def test_tool_call_with_text(self):
        content = "Some text before @tool2(123, key='value') and some text after."
        tool_names = ["tool1", "tool2"]
        result = parse_tool_call(content, tool_names)
        assert result[0] == "tool2"
        assert result[1] == "tool2(123, key='value')"
    
    def test_nested_parentheses(self):
        content = "@tool1(param1=[1, 2, (3, 4)], param2={'key': (5, 6)})"
        tool_names = ["tool1", "tool2"]
        result = parse_tool_call(content, tool_names)
        assert result[0] == "tool1"
        assert result[1] == "tool1(param1=[1, 2, (3, 4)], param2={'key': (5, 6)})"
    
    def test_tool_call_within_tool_call(self):
        content = "@tool2(func(arg1, arg2), '@tool1(param1=42)', key={'nested': (1, 2)})"
        tool_names = ["tool1", "tool2"]
        result = parse_tool_call(content, tool_names)
        assert result[0] == "tool2"
        assert result[1] == "tool2(func(arg1, arg2), '@tool1(param1=42)', key={'nested': (1, 2)})"

