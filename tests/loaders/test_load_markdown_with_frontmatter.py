"""Tests for load_markdown_with_frontmatter."""

# stdlib
from pathlib import Path

# third party
# local
from vindao_agents.loaders.load_markdown_with_frontmatter import load_markdown_with_frontmatter


class TestLoadMarkdownWithFrontmatter:
    def test_parse_valid_markdown(self, tmp_path: Path):
        md_content = """---
provider: openai
model: gpt-4
tools:
  - tools.file_ops
  - tools.bash
---
You are an honest assistant working in a self-extending system. You always answer with brutal honesty and value simplicity over unnecessary complexity.
"""
        md_file = tmp_path / "agent.md"
        md_file.write_text(md_content, encoding="utf-8")
        metadata, content = load_markdown_with_frontmatter(str(md_file))
        assert metadata["provider"] == "openai"
        assert metadata["model"] == "gpt-4"
        assert metadata["tools"] == ["tools.file_ops", "tools.bash"]
        assert "You are an honest assistant" in content

    def test_parse_missing_file(self):
        try:
            load_markdown_with_frontmatter("non_existent_file.md")
        except FileNotFoundError as e:
            assert "Markdown file not found" in str(e)

    def test_parse_invalid_markdown(self, tmp_path: Path):
        invalid_md_content = """---
provider: openai
model gpt-4
tools:  - tools.file_ops
  - tools.bash
---
This is invalid markdown frontmatter.
"""
        md_file = tmp_path / "invalid_agent.md"
        md_file.write_text(invalid_md_content, encoding="utf-8")
        try:
            load_markdown_with_frontmatter(str(md_file))
        except ValueError as e:
            assert "Failed to parse markdown frontmatter" in str(e)
