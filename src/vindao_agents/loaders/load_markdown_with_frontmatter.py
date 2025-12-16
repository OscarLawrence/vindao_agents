"""Markdown parser extracting YAML frontmatter and content for configuration files."""

# stdlib
from pathlib import Path
from typing import Dict, Any, Tuple

# third party
import frontmatter


def load_markdown_with_frontmatter(file_path: str) -> Tuple[Dict[str, Any], str]:
    """Load markdown files with YAML frontmatter into structured metadata and content."""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Markdown file not found: {file_path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        return post.metadata, post.content

    except Exception as e:
        raise ValueError(f"Failed to parse markdown frontmatter in {file_path}: {str(e)}")