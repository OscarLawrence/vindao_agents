"""Models for agent configuration and state management."""

# stdlib
from datetime import UTC, datetime

# third party
from pydantic import BaseModel, Field

# local
from vindao_agents.models.messages import MessageType


class AgentConfig(BaseModel):
    """Configuration settings for an agent."""

    name: str = Field(default="Momo", description="The name of the agent.")
    provider: str = Field(description="The LLM provider to use (e.g., 'openai', 'azure').")
    model: str = Field(description="The specific model to use from the provider (e.g., 'gpt-4').")
    tools: list[str] = Field(
        default=[], description="A list of tool identifiers which are loaded into the agents runtime."
    )
    max_iterations: int = Field(default=20, description="Maximum number of reasoning and tool usage iterations.")
    behavior: str = Field(default="", description="Behavioral instructions or personality traits for the agent.")
    auto_save: bool = Field(
        default=True, description="Whether to automatically save the agent's state after each interaction."
    )
    user_data_dir: str = Field(..., description="Directory for user-specific data.")
    system_prompt_data: dict = Field(default={}, description="Data to populate the system prompt template.")
    tools_with_source: bool = Field(
        default=True, description="Whether to include tool source code in the system prompt."
    )
    inference_adapter: str = Field(default="litellm", description="The inference adapter to use for LLM interactions.")
    parser: str = Field(default="at_syntax", description="The parser to use for detecting tool calls in LLM output.")


class AgentState(BaseModel):
    """Represents the state of an agent including its messages and tool usage history."""

    session_id: str = Field(..., description="Unique session identifier for the agent")
    created_at: float = Field(..., description="Timestamp when the agent state was created")
    updated_at: float = Field(..., description="Timestamp when the agent state was last updated")

    messages: list[MessageType] = Field(default=[], description="List of messages exchanged by the agent")

    def add_message(self, message: MessageType) -> None:
        """Add a new message to the agent's message history and update the timestamp."""
        self.messages.append(message)
        self.updated_at = datetime.now(UTC).timestamp()
