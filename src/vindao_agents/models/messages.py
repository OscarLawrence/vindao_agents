"""Data models for chat messages and conversation management."""


# stdlib
from typing import Literal
from uuid import uuid4 as uuid

# third party
from pydantic import BaseModel, Field

# local
from vindao_agents.models.tool import ToolCall

MessageRoleType = Literal["system", "user", "assistant", "tool"]

class BaseMessage(BaseModel):
    """Base class for all message types in the conversation."""
    content: str = Field(..., description="The content of the message")
    id: str = Field(default_factory=lambda: uuid().hex, description="Unique identifier for the message")

class SystemMessage(BaseMessage):
    """Represents system instructions provided to the agent at conversation start."""
    role: MessageRoleType = Field(default="system", description="The role of the message, fixed as 'system'")

class UserMessage(BaseMessage):
    """Represents user input message in the conversation."""
    role: MessageRoleType = Field(default="user", description="The role of the message, fixed as 'user'")
    name: str | None =  Field(default=None, description="The name of the sender if applicable")

class AssistantMessage(BaseMessage):
    """Represents agent-generated response with optional reasoning and tool calls."""
    role: MessageRoleType = Field(default="assistant", description="The role of the message, fixed as 'assistant'")
    reasoning_content: str | None = Field(default=None, description="The reasoning content if applicable")
    name: str | None =  Field(default=None, description="The name of the sender if applicable")
    tool_call: ToolCall | None = Field(default=None, description="The tool call if applicable")

class ToolMessage(BaseMessage):
    """Represents tool execution result returned to the conversation."""
    role: MessageRoleType = Field(default="tool", description="The role of the message, fixed as 'tool'")
    name: str =  Field(..., description="The name of the sender if applicable")
    tool_call: ToolCall = Field(..., description="The tool call if applicable")

MessageType = SystemMessage | UserMessage | AssistantMessage | ToolMessage