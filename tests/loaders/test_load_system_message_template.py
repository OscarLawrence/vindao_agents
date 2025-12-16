"""Tests for load_system_message_template."""

# stdlib
from pathlib import Path

# third party
import pytest

# local
from vindao_agents.loaders.load_system_message_template import load_system_message_template


class TestLoadSystemMessageTemplate:
    def test_load_default_template(self, tmp_path: Path):
        user_data_dir = tmp_path / "vindao_agents"
        prompts_dir = user_data_dir / "prompts" / "system_message"
        prompts_dir.mkdir(parents=True, exist_ok=True)

        # Create a default prompt file
        default_prompt_path = prompts_dir / "default.prompt"
        default_content = "This is the default system message."
        default_prompt_path.write_text(default_content, encoding='utf-8')

        # Load the template for a non-existing model
        loaded_template = load_system_message_template("non_existing_model", user_data_dir)
        assert loaded_template == default_content

    def test_load_model_specific_template(self, tmp_path: Path):
        user_data_dir = tmp_path / "vindao_agents"
        prompts_dir = user_data_dir / "prompts" / "system_message"
        prompts_dir.mkdir(parents=True, exist_ok=True)

        # Create a model-specific prompt file
        model_prompt_path = prompts_dir / "gpt-4.prompt"
        model_content = "This is the GPT-4 system message."
        model_prompt_path.write_text(model_content, encoding='utf-8')

        # Load the template for the existing model
        loaded_template = load_system_message_template("gpt-4", user_data_dir)
        assert loaded_template == model_content
