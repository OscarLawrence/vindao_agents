# stdlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vindao_agents.Agent import Agent


class AgentStore(ABC):
    def __init__(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def save(self, agent: "Agent", path: str | Path | None = None) -> None:
        """Save the state of the agent."""
        pass
