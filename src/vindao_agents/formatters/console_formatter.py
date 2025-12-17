"""Console formatter for displaying agent events."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vindao_agents.models.tool import ToolCall
    from vindao_agents.utils import AgentLogger


class ConsoleFormatter:
    """Formats and displays agent events to console.

    This class handles the presentation of agent output including:
    - Streaming content and reasoning chunks
    - Tool call results
    - Session messages

    It separates display logic from agent orchestration, allowing
    the Agent class to remain I/O agnostic.
    """

    def __init__(self, logger: AgentLogger):
        """Initialize the console formatter.

        Args:
            logger: Logger instance for non-streaming messages
        """
        self.logger = logger

    def display_event(self, chunk: str | ToolCall, chunk_type: str) -> None:
        """Display an agent event to the console.

        Args:
            chunk: The content to display (text chunk or ToolCall)
            chunk_type: Type of event ("content", "reasoning", or "tool")
        """
        if chunk_type in ["content", "reasoning"]:
            # Stream text chunks without newlines
            sys.stdout.write(str(chunk))
            sys.stdout.flush()
        elif chunk_type == "tool":
            # Format and display tool call results
            sys.stdout.write(f" =>\n{chunk.result}\n")
            sys.stdout.flush()

    def display_message(self, message: str) -> None:
        """Display a non-streaming message.

        Args:
            message: The message to display
        """
        self.logger.info(message)

    def display_newline(self) -> None:
        """Display a newline after agent response."""
        self.logger.info("")
