# standard library imports
from typing import Callable
from datetime import datetime, timezone

# third-party imports
from pydantic import BaseModel, Field

# local imports
from vindao_agents.models.messages import Message


class AgentConfig(BaseModel):
    """Configuration settings for an agent."""

    provider: str = Field(description="The LLM provider to use (e.g., 'openai', 'azure').")
    model: str = Field(description="The specific model to use from the provider (e.g., 'gpt-4').")
    tools: list[str | Callable] = Field(default=[], description="A list of tools available to the agent. Can be tool identifiers or callable functions.")
    max_iterations: int = Field(default=20, description="Maximum number of reasoning and tool usage iterations.")
    behavior: str = Field(default="", description="Behavioral instructions or personality traits for the agent.")
    auto_save: bool = Field(default=True, description="Whether to automatically save the agent's state after each interaction.")

class AgentState(BaseModel):
    """Represents the state of an agent including its messages and tool usage history."""
    session_id: str = Field(..., description="Unique session identifier for the agent")
    created_at: float = Field(..., description="Timestamp when the agent state was created")
    updated_at: float = Field(..., description="Timestamp when the agent state was last updated")
    
    messages: list = Field(default=[], description="List of messages exchanged by the agent")

    def add_message(self, message: Message) -> None:
        """Add a new message to the agent's message history and update the timestamp."""
        self.messages.append(message)
        self.updated_at = datetime.now(timezone.utc).timestamp()
