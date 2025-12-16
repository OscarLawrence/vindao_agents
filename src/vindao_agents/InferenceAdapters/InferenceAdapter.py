"""Abstract base class for inference adapters."""

# stdlib
from typing import Generator, Tuple, Literal, AsyncGenerator
from abc import ABC, abstractmethod

# local
from vindao_agents.models.messages import MessageType

class InferenceAdapter(ABC):
    @abstractmethod
    def complete_chat(self, messages: list[MessageType], max_retries: int = 5, retry: int = 0) -> Generator[Tuple[str, Literal['reasoning', 'content']], None, None]:
        """Abstract method for chat completion."""
        pass
