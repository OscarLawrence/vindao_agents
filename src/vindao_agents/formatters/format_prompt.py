"""Utility functions for loading and formatting prompt templates."""

# third party
from jinja2 import Template


def format_prompt(text: str, data: dict) -> str:
    """Format a prompt template with the given data."""
    template = Template(text)
    return template.render(**data)

class TestFormatPrompt:

    def test_format_prompt(self):
        template = "Hello, {{ name }}! Welcome to {{ place }}."
        data = {"name": "Alice", "place": "Wonderland"}
        formatted = format_prompt(template, data)
        assert formatted == "Hello, Alice! Welcome to Wonderland."