"""Markdown parser extracting YAML frontmatter and content for configuration files."""

import frontmatter
from pathlib import Path
from typing import Dict, Any, Tuple


def parse_markdown(file_path: str) -> Tuple[Dict[str, Any], str]:
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
    

def test_parse_markdown():
    import tempfile

    md_content = """---
provider: openai
model: gpt-4.1-nano
tools:
  - tool1
  - tool2
max_iterations: 10
---
This is the behavior description of the agent.
It can span multiple lines.
"""
    with tempfile.NamedTemporaryFile('w+', suffix='.md', delete=False) as tmp:
        tmp.write(md_content)
        tmp_path = tmp.name

    metadata, content = parse_markdown(tmp_path)
    assert metadata == {
        "provider": "openai",
        "model": "gpt-4.1-nano",
        "tools": ["tool1", "tool2"],
        "max_iterations": 10,
    }
    assert content == """This is the behavior description of the agent.\nIt can span multiple lines."""
    Path(tmp_path).unlink()  # Clean up temporary file