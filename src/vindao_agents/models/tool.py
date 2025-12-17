"""Data model for tool call representation in agent interactions."""

# stdlib
from uuid import uuid4 as uuid

# third party
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """Represents result of tool execution with metadata for agent conversation tracking."""

    name: str = Field(description="Name of the tool executed")
    call: str = Field(description="The exact tool call made")
    id: str = Field(default_factory=lambda: uuid().hex, description="Unique identifier for the tool call")
    result: str | None = Field(default=None, description="Result of the tool call execution")
