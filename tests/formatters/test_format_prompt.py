"""Tests for format_prompt."""

# third party
import pytest

# local
from vindao_agents.formatters.format_prompt import format_prompt


class TestFormatPrompt:

    def test_format_prompt(self):
        template = "Hello, {{ name }}! Welcome to {{ place }}."
        data = {"name": "Alice", "place": "Wonderland"}
        formatted = format_prompt(template, data)
        assert formatted == "Hello, Alice! Welcome to Wonderland."
