"""Centralized path resolution utilities for vindao_agents framework."""
from pathlib import Path


def resolve_path(filename: str, search_dirs: list[str | Path]) -> Path:
    """
    Resolve a file path by searching through directories in priority order.

    Args:
        filename: The filename to search for
        search_dirs: List of directories to search, in priority order

    Returns:
        Path: The resolved absolute path to the file

    Raises:
        FileNotFoundError: If the file is not found in any of the search directories
    """
    for directory in search_dirs:
        candidate = Path(directory) / filename
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        f"Could not find '{filename}' in any of the following directories: "
        f"{[str(Path(d)) for d in search_dirs]}"
    )


def resolve_path_with_fallbacks(
    filenames: list[str],
    search_dirs: list[str | Path]
) -> Path:
    """
    Resolve a file path by trying multiple filenames across multiple directories.

    This function searches for the first filename that exists, trying each filename
    in all directories before moving to the next filename.

    Args:
        filenames: List of filenames to try, in priority order
        search_dirs: List of directories to search

    Returns:
        Path: The resolved absolute path to the first file found

    Raises:
        FileNotFoundError: If none of the files are found in any directory
    """
    for filename in filenames:
        for directory in search_dirs:
            candidate = Path(directory) / filename
            if candidate.exists():
                return candidate

    raise FileNotFoundError(
        f"Could not find any of {filenames} in any of the following directories: "
        f"{[str(Path(d)) for d in search_dirs]}"
    )
