"""Logging utilities for the vindao_agents framework."""
import logging
from typing import Protocol


class AgentLogger(Protocol):
    """Protocol for agent logging interface."""

    def debug(self, msg: str, *args, **kwargs) -> None:
        """Log a debug message."""
        ...

    def info(self, msg: str, *args, **kwargs) -> None:
        """Log an info message."""
        ...

    def warning(self, msg: str, *args, **kwargs) -> None:
        """Log a warning message."""
        ...

    def error(self, msg: str, *args, **kwargs) -> None:
        """Log an error message."""
        ...


def get_default_logger(name: str = "vindao_agents") -> logging.Logger:
    """
    Get the default logger for the vindao_agents framework.

    Args:
        name: The logger name. Defaults to "vindao_agents".

    Returns:
        A configured Logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
