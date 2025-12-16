"""System message template loader for AI agents."""
# stdlib
from pathlib import Path

def load_system_message_template(model: str, user_data_dir: str | Path) -> str:
    user_path = Path(user_data_dir) / 'prompts' / 'system_message'
    template_file = user_path / f"{model}.prompt"
    template = None
    if not template_file.exists():
        template_file = user_path / "default.prompt"
        if not template_file.exists():
            default_path = Path(__file__).parent.parent / 'prompts' / 'system_message' / "default.prompt"
            template = default_path.read_text(encoding='utf-8')
        else:
            template = template_file.read_text(encoding='utf-8')
    else:
        template = template_file.read_text(encoding='utf-8')
    return template