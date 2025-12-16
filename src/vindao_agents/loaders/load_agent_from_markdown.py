
# stdlib
from pathlib import Path

# local
from vindao_agents.loaders import load_markdown_with_frontmatter


def load_agent_from_markdown(path: Path | str) -> dict:
    """Load an Agent instance from a markdown file with frontmatter."""
    path = Path(path)
    metadata, behavior = load_markdown_with_frontmatter(path)
    return {
        "name": path.stem,
        "provider": metadata.get("provider", "ollama"),
        "model": metadata.get("model", "qwen2.5:0.5b"),
        "tools": metadata.get("tools", []),
        "behavior": behavior,
        "max_iterations": metadata.get("max_iterations", 15),
        "auto_save": metadata.get("auto_save", True),
        "user_data_dir": metadata.get("user_data_dir", Path.cwd() / ".vindao_agents"),
        "system_prompt_data": metadata.get("system_prompt_data", {}),
        "tools_with_source": metadata.get("tools_with_source", True),
    }
