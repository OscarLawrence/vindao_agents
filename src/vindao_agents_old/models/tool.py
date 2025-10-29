# standard library imports
from typing import Dict, Any
from uuid import uuid4 as uuid

# third-party imports
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """Represents result of tool execution with metadata for agent conversation tracking."""
    
    name: str = Field(description="Name of the tool executed")
    call: str = Field(description="The exact tool call made")
    id: str = Field(default=uuid().hex, description="Unique identifier for the tool call")
    result: str | None = Field(default=None, description="Result of the tool call execution")

    