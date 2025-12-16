"""Abstract base class for inference adapters."""

# stdlib
from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import Literal

# local
from vindao_agents.models.messages import MessageType


class InferenceAdapter(ABC):
    @abstractmethod
    def complete_chat(self, messages: list[MessageType], max_retries: int = 5, retry: int = 0) -> Generator[tuple[str, Literal['reasoning', 'content']], None, None]:
        """Abstract method for chat completion."""
        pass
