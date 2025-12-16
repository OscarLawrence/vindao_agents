"""Utility functions for loading and formatting prompt templates."""

# third party
from jinja2 import Template


def format_prompt(text: str, data: dict) -> str:
    """Format a prompt template with the given data."""
    template = Template(text)
    return template.render(**data)
