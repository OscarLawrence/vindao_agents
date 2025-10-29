"""Data models for chat messages and conversation management."""



# Standard library imports
from typing import Literal

# Third-party imports
from pydantic import BaseModel, Field

# Local import
from vindao_agents.models.tool import ToolCall



MessageRoleType = Literal["system", "user", "assistant", "tool"]
"""Type representing different message roles in a conversation."""


class SystemMessage(BaseModel):
    """Represents system instructions provided to the agent at conversation start."""
    role: MessageRoleType = Field(default="system")
    content: str = Field(..., description="The content of the system message")

class UserMessage(BaseModel):
    """Represents user input message in the conversation."""
    role: MessageRoleType = Field(default="user")
    content: str = Field(..., description="The content of the user message")
    name: str | None =  Field(default=None, description="The name of the sender if applicable")

class AssistantMessage(BaseModel):
    """Represents agent-generated response with optional reasoning and tool calls."""
    role: MessageRoleType = Field(default="assistant")
    content: str = Field(..., description="The content of the assistant message")
    reasoning_content: str | None = Field(default=None, description="The reasoning content if applicable")
    name: str | None =  Field(default=None, description="The name of the sender if applicable")
    tool_call: ToolCall | None = Field(default=None, description="The tool call if applicable")

class ToolMessage(BaseModel):
    """Represents tool execution result returned to the conversation."""
    role: MessageRoleType = Field(default="tool")
    content: str = Field(..., description="The content of the tool message")
    name: str | None =  Field(default=None, description="The name of the sender if applicable")
    tool_call: ToolCall | None = Field(default=None, description="The tool call if applicable")

Message = SystemMessage | UserMessage | AssistantMessage | ToolMessage