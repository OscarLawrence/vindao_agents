"""Tests for the logging utility module."""
import logging
from unittest.mock import MagicMock, patch

from vindao_agents.utils.logger import AgentLogger, get_default_logger


class TestAgentLoggerProtocol:
    """Tests for the AgentLogger Protocol."""

    def test_protocol_has_required_methods(self):
        """Test that AgentLogger protocol defines required methods."""
        # Verify protocol has the expected methods
        assert hasattr(AgentLogger, 'debug')
        assert hasattr(AgentLogger, 'info')
        assert hasattr(AgentLogger, 'warning')
        assert hasattr(AgentLogger, 'error')

    def test_standard_logger_implements_protocol(self):
        """Test that Python's standard Logger implements the AgentLogger protocol."""
        logger = logging.getLogger("test")

        # Standard logger should have all required methods
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')

        # These methods should be callable
        assert callable(logger.debug)
        assert callable(logger.info)
        assert callable(logger.warning)
        assert callable(logger.error)

    def test_mock_logger_implements_protocol(self):
        """Test that a mock logger can implement the AgentLogger protocol."""
        mock_logger = MagicMock(spec=AgentLogger)

        # Mock should have all protocol methods
        assert hasattr(mock_logger, 'debug')
        assert hasattr(mock_logger, 'info')
        assert hasattr(mock_logger, 'warning')
        assert hasattr(mock_logger, 'error')

        # Can call methods without errors
        mock_logger.info("test message")
        mock_logger.debug("debug message")
        mock_logger.warning("warning message")
        mock_logger.error("error message")

        # Verify methods were called
        mock_logger.info.assert_called_once_with("test message")
        mock_logger.debug.assert_called_once_with("debug message")
        mock_logger.warning.assert_called_once_with("warning message")
        mock_logger.error.assert_called_once_with("error message")


class TestGetDefaultLogger:
    """Tests for the get_default_logger function."""

    def test_returns_logger_instance(self):
        """Test that get_default_logger returns a Logger instance."""
        logger = get_default_logger()
        assert isinstance(logger, logging.Logger)

    def test_default_logger_name(self):
        """Test that the default logger has the correct name."""
        logger = get_default_logger()
        assert logger.name == "vindao_agents"

    def test_custom_logger_name(self):
        """Test that get_default_logger accepts a custom name."""
        logger = get_default_logger("custom_name")
        assert logger.name == "custom_name"

    def test_logger_has_handler(self):
        """Test that the logger has at least one handler configured."""
        logger = get_default_logger("test_handler")
        assert len(logger.handlers) > 0

    def test_logger_has_stream_handler(self):
        """Test that the logger uses a StreamHandler."""
        logger = get_default_logger("test_stream")
        assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)

    def test_logger_default_level_is_info(self):
        """Test that the logger's default level is INFO."""
        logger = get_default_logger("test_level")
        assert logger.level == logging.INFO

    def test_logger_formatter_simple_format(self):
        """Test that the logger uses a simple message-only formatter."""
        logger = get_default_logger("test_format")
        handler = logger.handlers[0]
        formatter = handler.formatter

        # Create a log record and format it
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None
        )
        formatted = formatter.format(record)

        # Should only contain the message, no timestamp or level
        assert formatted == "Test message"

    def test_idempotent_logger_creation(self):
        """Test that calling get_default_logger multiple times with same name returns configured logger."""
        # First call sets up the logger
        logger1 = get_default_logger("idempotent_test")
        handler_count1 = len(logger1.handlers)

        # Second call should return the same logger without adding more handlers
        logger2 = get_default_logger("idempotent_test")
        handler_count2 = len(logger2.handlers)

        assert logger1 is logger2
        assert handler_count1 == handler_count2

    def test_logger_can_log_messages(self):
        """Test that the logger can actually log messages."""
        logger = get_default_logger("test_logging")

        # Mock the handler to capture log output
        with patch.object(logger.handlers[0], 'emit') as mock_emit:
            logger.info("Test info message")
            logger.warning("Test warning message")
            logger.error("Test error message")

            # Verify emit was called
            assert mock_emit.call_count == 3

    def test_logger_debug_not_logged_by_default(self):
        """Test that DEBUG messages are not logged with INFO level."""
        logger = get_default_logger("test_debug_level")

        with patch.object(logger.handlers[0], 'emit') as mock_emit:
            logger.debug("Debug message")

            # Should not be emitted because level is INFO
            mock_emit.assert_not_called()

    def test_logger_can_be_reconfigured(self):
        """Test that the logger's level can be changed after creation."""
        logger = get_default_logger("test_reconfig")

        # Change level to DEBUG
        logger.setLevel(logging.DEBUG)

        with patch.object(logger.handlers[0], 'emit') as mock_emit:
            logger.debug("Debug message")

            # Should now be emitted
            mock_emit.assert_called_once()

    def test_multiple_loggers_with_different_names(self):
        """Test that different logger names create different loggers."""
        logger1 = get_default_logger("logger_one")
        logger2 = get_default_logger("logger_two")

        assert logger1 is not logger2
        assert logger1.name == "logger_one"
        assert logger2.name == "logger_two"

    def test_logger_accepts_format_args(self):
        """Test that logger methods accept formatting arguments."""
        logger = get_default_logger("test_format_args")

        # Should not raise any errors
        logger.info("Message with %s", "args")
        logger.info("Message with %s and %d", "string", 42)
        logger.info("Message with kwargs", extra={"custom": "data"})
