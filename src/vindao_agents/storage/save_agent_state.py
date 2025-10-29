"""Module for saving the state of an agent to persistent storage."""

# stdlib
import json
from pathlib import Path


def save_agent_state(agent, path: str | Path | None = None) -> None:
    """Save the agent's state to a file."""
    
    if path is None:
        path = Path(agent.config.user_data_dir) / 'sessions' / f"{agent.state.session_id}_state.json"
    else:
        path = Path(path)

    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        'state': agent.state.model_dump(),
        'config': agent.config.model_dump(),
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=4)