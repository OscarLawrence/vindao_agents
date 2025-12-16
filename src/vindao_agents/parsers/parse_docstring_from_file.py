"""Parse docstring from Python file using AST."""
# stdlib
from pathlib import Path
import ast


def parse_docstring_from_file(file_path: Path) -> str | None:
    """Extract docstring from a Python file without executing it."""
    try:
        source = file_path.read_text(encoding='utf-8')
        tree = ast.parse(source)
        return ast.get_docstring(tree)
    except Exception:
        return None