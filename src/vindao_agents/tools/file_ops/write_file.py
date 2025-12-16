"""A tool for writing content to a specified file."""

from pathlib import Path


def write_file(path: str, content: str) -> str:
    """Write content to a specified file."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"Content written to {p.resolve().as_posix()}"
