"""Abstract base class for tool call parsers."""

# stdlib
from abc import ABC, abstractmethod


class ToolParser(ABC):
    """Abstract base class for parsing tool calls from LLM-generated content.

    Parsers are responsible for detecting and extracting tool calls from text
    in various formats (e.g., @syntax, XML-style, JSON-style, etc.).
    """

    @abstractmethod
    def parse(self, content: str, tool_names: list[str]) -> tuple[str, str] | None:
        """Parse a tool call from the given content.

        Args:
            content: The text content to parse for tool calls
            tool_names: List of available tool names to match against

        Returns:
            A tuple of (tool_name, tool_call) if a tool call is found, None otherwise.
            The tool_call should be in a format ready for execution (e.g., "tool_name(args)")
        """
        pass

    @abstractmethod
    def get_instructions(self) -> str:
        """Get the instructions for the LLM on how to format tool calls.

        Returns:
            A string containing instructions that will be injected into the system prompt
            to teach the LLM how to format tool calls for this parser.
        """
        pass
