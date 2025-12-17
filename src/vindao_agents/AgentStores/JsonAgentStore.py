# stdlib
import json
from pathlib import Path
from typing import TYPE_CHECKING

# local
from .AgentStore import AgentStore

if TYPE_CHECKING:
    from vindao_agents.Agent import Agent


class JsonAgentStore(AgentStore):
    def save(self, agent: "Agent", path: str | Path | None = None) -> None:
        """Save the state of the agent as a JSON file."""
        if path is None:
            path = Path(agent.config.user_data_dir) / f"{agent.state.session_id}.json"
        else:
            path = Path(path)

        data = {
            "config": agent.config.model_dump(),
            "state": agent.state.model_dump(),
        }

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
