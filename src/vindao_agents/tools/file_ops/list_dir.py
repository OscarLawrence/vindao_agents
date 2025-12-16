"""List directory contents with docstrings for Python files and packages."""
# stdlib
from pathlib import Path

# vindao_agents
from vindao_agents.parsers import parse_docstring_from_file


def list_dir(path: str = ".", show_hidden: bool = False, ignore: list[str] = ["__pycache__"]) -> str:
    """List files and directories in the given path. For Python files and packages, include their docstrings."""
    result = []
    p = Path(path)

    # If the path itself is a package, show its docstring at the top
    init_file = p / "__init__.py"
    if init_file.exists():
        doc = parse_docstring_from_file(init_file)
        if doc:
            result.append(f"{doc}\n")
    for item in p.iterdir():
        if not show_hidden and item.name.startswith("."):
            continue
        if item.name in ignore or item.name == "__init__.py":
            continue
        item_str = item.as_posix()
        if item.is_dir():
            item_str += "/"
            # load package docstring if possible
            init_file = item / "__init__.py"
            if init_file.exists():
                doc = parse_docstring_from_file(init_file)
                if doc:
                    item_str += f" - {doc}"
        elif item.is_symlink():
            item_str += "@"
        elif item.suffix == ".py":
            # load module docstring if possible
            doc = parse_docstring_from_file(item)
            if doc:
                item_str += f" - {doc}"
        result.append(item_str)
    return "\n".join(result)