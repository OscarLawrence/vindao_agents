"""Tests for ConsoleFormatter."""
import sys
from io import StringIO
from unittest.mock import Mock, patch
import pytest

from vindao_agents.formatters import ConsoleFormatter
from vindao_agents.models.tool import ToolCall


class TestConsoleFormatter:
    """Test suite for ConsoleFormatter class."""

    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger for testing."""
        logger = Mock()
        logger.info = Mock()
        logger.debug = Mock()
        logger.warning = Mock()
        logger.error = Mock()
        return logger

    @pytest.fixture
    def formatter(self, mock_logger):
        """Create a ConsoleFormatter instance with mock logger."""
        return ConsoleFormatter(mock_logger)

    def test_init(self, mock_logger):
        """Test ConsoleFormatter initialization."""
        formatter = ConsoleFormatter(mock_logger)
        assert formatter.logger is mock_logger

    def test_display_event_content(self, formatter):
        """Test displaying content chunks."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            formatter.display_event("Hello", "content")
            assert mock_stdout.getvalue() == "Hello"

    def test_display_event_reasoning(self, formatter):
        """Test displaying reasoning chunks."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            formatter.display_event("Thinking...", "reasoning")
            assert mock_stdout.getvalue() == "Thinking..."

    def test_display_event_tool(self, formatter):
        """Test displaying tool call results."""
        tool_call = ToolCall(
            name="test_tool",
            call="test_tool(arg='value')",
            result="Tool executed successfully"
        )
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            formatter.display_event(tool_call, "tool")
            output = mock_stdout.getvalue()
            assert " =>\n" in output
            assert "Tool executed successfully" in output
            assert output.endswith("\n")

    def test_display_event_multiple_content_chunks(self, formatter):
        """Test displaying multiple content chunks in sequence."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            formatter.display_event("Hello ", "content")
            formatter.display_event("World", "content")
            formatter.display_event("!", "content")
            assert mock_stdout.getvalue() == "Hello World!"

    def test_display_message(self, formatter, mock_logger):
        """Test displaying non-streaming messages."""
        formatter.display_message("Test message")
        mock_logger.info.assert_called_once_with("Test message")

    def test_display_newline(self, formatter, mock_logger):
        """Test displaying newline."""
        formatter.display_newline()
        mock_logger.info.assert_called_once_with("")

    def test_display_event_streaming_without_newlines(self, formatter):
        """Test that streaming chunks don't add newlines."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            formatter.display_event("Line1", "content")
            formatter.display_event("Line2", "content")
            output = mock_stdout.getvalue()
            # Should be concatenated without newlines between them
            assert output == "Line1Line2"
            assert output.count("\n") == 0

    def test_display_event_tool_formatting(self, formatter):
        """Test that tool results are properly formatted with arrow."""
        tool_call = ToolCall(
            name="read_file",
            call="read_file(path='/tmp/test.txt')",
            result="File contents here"
        )
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            formatter.display_event(tool_call, "tool")
            output = mock_stdout.getvalue()
            # Check for arrow formatting
            assert output.startswith(" =>")
            assert "File contents here" in output

    def test_display_message_multiple_calls(self, formatter, mock_logger):
        """Test multiple display_message calls."""
        formatter.display_message("Message 1")
        formatter.display_message("Message 2")
        formatter.display_message("Message 3")
        assert mock_logger.info.call_count == 3

    def test_formatter_with_empty_content(self, formatter):
        """Test displaying empty content."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            formatter.display_event("", "content")
            assert mock_stdout.getvalue() == ""

    def test_formatter_with_special_characters(self, formatter):
        """Test displaying content with special characters."""
        special_text = "Special chars: \n\t\r\\"
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            formatter.display_event(special_text, "content")
            assert mock_stdout.getvalue() == special_text

    def test_formatter_preserves_logger_instance(self, mock_logger):
        """Test that formatter preserves the logger instance."""
        formatter = ConsoleFormatter(mock_logger)
        assert formatter.logger is mock_logger
        # Verify it's the exact same instance, not a copy
        assert id(formatter.logger) == id(mock_logger)
