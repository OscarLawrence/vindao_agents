"""Tests for format_exception."""

# third party
import pytest

# local
from vindao_agents.formatters.format_exception import format_exception


class TestFormatException:

    def test_without_function(self):
        try:
            1 / 0
        except Exception as e:
            formatted = format_exception(e)
            assert "ZeroDivisionError" in formatted
            assert "1 / 0" in formatted

    def test_with_function(self):
        def faulty_function():
            return 1 / 0

        try:
            faulty_function()
        except Exception as e:
            formatted = format_exception(e, faulty_function)
            assert "ZeroDivisionError" in formatted
            assert "faulty_function" in formatted
            assert "1 / 0" in formatted

    def test_no_duplicate_exception_message(self):
        """Test that exception message doesn't appear twice (Issue #10)."""
        try:
            raise ValueError("test error message")
        except Exception as e:
            formatted = format_exception(e)
            # Count occurrences of the exception message
            count = formatted.count("ValueError: test error message")
            assert count == 1, f"Exception message appears {count} times, expected 1"
