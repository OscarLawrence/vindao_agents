"""Formatter for exceptions into readable strings."""

# stdlib
import traceback
from collections.abc import Callable


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

    return "".join(tb_lines).strip()
