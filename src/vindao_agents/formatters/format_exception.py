"""Formatter for exceptions into readable strings."""

# stdlib
from typing import Callable
import traceback


def format_exception(exc: Exception, function: Callable | None = None) -> str:
    """Format an exception into a readable string."""
    tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)

    if function:
        # filter traceback to only include frames from the given function
        filtered_lines = []
        capture = False
        for line in tb_lines:
            if function.__name__ in line:
                capture = True
            if capture:
                filtered_lines.append(line)
            if line.strip() == "":
                capture = False
        tb_lines = filtered_lines
    
    return "".join(tb_lines).strip() + f"{type(exc).__name__}: {str(exc)}"


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