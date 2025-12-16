"""System message template loader for AI agents."""
# stdlib
from pathlib import Path

# local
from vindao_agents.utils import resolve_path_with_fallbacks


def load_system_message_template(model: str, user_data_dir: str | Path) -> str:
    """
    Load a system message template for the given model.

    Searches in priority order:
    1. {user_data_dir}/prompts/system_message/{model}.prompt
    2. {user_data_dir}/prompts/system_message/default.prompt
    3. {package}/prompts/system_message/default.prompt

    Args:
        model: The model name to load a template for
        user_data_dir: The user data directory to search in

    Returns:
        str: The template content
    """
    filenames = [f"{model}.prompt", "default.prompt"]
    search_dirs = [
        Path(user_data_dir) / 'prompts' / 'system_message',
        Path(__file__).parent.parent / 'prompts' / 'system_message'
    ]

    template_file = resolve_path_with_fallbacks(filenames, search_dirs)
    return template_file.read_text(encoding='utf-8')
