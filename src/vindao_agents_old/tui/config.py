"""User configuration management for vindao_agents."""

import json
from pathlib import Path
from typing import Any


class Config:
    """Manages user configuration stored in ~/.vindao_agents/config.json"""

    def __init__(self):
        self.config_dir = Path.home() / ".vindao_agents"
        self.config_file = self.config_dir / "config.json"
        self.agents_dir = self.config_dir / "agents"
        self.tools_dir = self.config_dir / "tools"
        self.sessions_dir = self.config_dir / "sessions"
        self._config = self._load()

    def _load(self) -> dict[str, Any]:
        """Load configuration from disk or create default."""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._get_defaults()

    def _get_defaults(self) -> dict[str, Any]:
        """Return default configuration."""
        return {
            "first_run": True,
            "default_provider": "openai",
            "default_model": "gpt-4.1-nano",
            "theme": "dark",
            "show_reasoning": True,
            "auto_save": True,
        }

    def save(self) -> None:
        """Save configuration to disk."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=4)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value and save."""
        self._config[key] = value
        self.save()

    def is_first_run(self) -> bool:
        """Check if this is the first time the TUI is being run."""
        return self.get("first_run", True)

    def mark_setup_complete(self) -> None:
        """Mark the initial setup as complete."""
        self.set("first_run", False)

    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        self.tools_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def get_agent_files(self) -> list[Path]:
        """Get list of agent markdown files."""
        if not self.agents_dir.exists():
            return []
        return sorted(self.agents_dir.glob("*.md"))

    def get_tool_modules(self) -> list[Path]:
        """Get list of tool Python modules."""
        if not self.tools_dir.exists():
            return []
        return sorted(self.tools_dir.glob("*.py"))
