"""Default parser implementation using @-syntax for tool calls."""

# stdlib
import re

# local
from .ToolParser import ToolParser


class AtSyntaxParser(ToolParser):
    """Parser for tool calls in the format @tool_name(...).

    This is the default parser implementation that detects tool calls
    using the @-syntax convention (e.g., @read_file('path/to/file.txt')).
    """

    def parse(self, content: str, tool_names: list[str]) -> tuple[str, str] | None:
        """Parse a tool call using @-syntax from the given content.

        Args:
            content: The text content to parse for tool calls
            tool_names: List of available tool names to match against

        Returns:
            A tuple of (tool_name, tool_call) if found, where tool_call
            has the @ symbol removed. Returns None if no tool call is detected.

        Examples:
            >>> parser = AtSyntaxParser()
            >>> parser.parse("Let me @read_file('test.txt')", ["read_file"])
            ('read_file', "read_file('test.txt')")
        """
        # Pattern to match @{tool_name}(...) where tool_name is in tool_names
        pattern = r"@(" + "|".join(re.escape(name) for name in tool_names) + r")\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)"
        match = re.search(pattern, content)

        if match:
            tool_name = match.group(1)
            tool_call = match.group(0)[1:]  # Remove the '@' symbol
            return tool_name, tool_call
        return None

    def get_instructions(self) -> str:
        """Get instructions for the LLM on how to format tool calls using @-syntax.

        Returns:
            Instructions explaining the @-syntax format for tool calls.
        """
        return """You can call the functions anywhere within your response like a normal python function, but need to prepend your call with a @ symbol.
Functions will be executed immediately and you will be reinvoked with the functions response available
You will be reinvoked until no function call is detected within your response
You can disable tool calling by starting your response with: @DISABLE_TOOL_CALL@

## Example function call

def read_file(file_path: str) -> str:
    '''Reads the content of a file and returns it as a string.'''

Usage:
@read_file('README.md')"""
