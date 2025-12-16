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
