"""Markdown parser extracting YAML frontmatter and content for configuration files."""

# stdlib
from pathlib import Path
from typing import Dict, Any, Tuple

# third party
import frontmatter


def parse_markdown_with_frontmatter(file_path: str) -> Tuple[Dict[str, Any], str]:
    """Parse markdown files with YAML frontmatter into structured metadata and content."""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Markdown file not found: {file_path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        return post.metadata, post.content
    
    except Exception as e:
        raise ValueError(f"Failed to parse markdown frontmatter in {file_path}: {str(e)}")
    

class TestParseMarkdownWithFrontmatter:
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
        md_file.write_text(md_content, encoding='utf-8')    
        metadata, content = parse_markdown_with_frontmatter(str(md_file))
        assert metadata['provider'] == 'openai'
        assert metadata['model'] == 'gpt-4'
        assert metadata['tools'] == ['tools.file_ops', 'tools.bash']
        assert "You are an honest assistant" in content

    def test_parse_missing_file(self):
        try:
            parse_markdown_with_frontmatter("non_existent_file.md")
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
        md_file.write_text(invalid_md_content, encoding='utf-8')    
        try:
            parse_markdown_with_frontmatter(str(md_file))
        except ValueError as e:
            assert "Failed to parse markdown frontmatter" in str(e)
            