"""Read file tool."""


def read_file(path: str) -> str:
    """Read the content of a specified file."""
    from pathlib import Path

    return Path(path).read_text()
