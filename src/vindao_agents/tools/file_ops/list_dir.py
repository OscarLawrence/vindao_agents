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


class TestListDir:
    """Tests for list_dir function."""

    def test_ignore_and_hidden(self, tmp_path: Path):
        """Test filtering of hidden files and ignored directories."""
        # Setup
        (tmp_path / "visible_file.txt").write_text("visible")
        (tmp_path / ".hidden_file.txt").write_text("hidden")
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "normal_dir").mkdir()

        # Test without hidden files
        output = list_dir(tmp_path.as_posix(), show_hidden=False)
        assert "visible_file.txt" in output
        assert ".hidden_file.txt" not in output
        assert "__pycache__" not in output
        assert "normal_dir/" in output

        # Test with hidden files
        output = list_dir(tmp_path.as_posix(), show_hidden=True)
        assert "visible_file.txt" in output
        assert ".hidden_file.txt" in output
        assert "__pycache__" not in output
        assert "normal_dir/" in output

    def test_python_module_with_docstring(self, tmp_path: Path):
        """Test that Python module docstrings are displayed."""
        # Setup
        module_path = tmp_path / "sample_module.py"
        module_path.write_text('"""This is a sample module."""\n\nx = 42')

        # Test
        output = list_dir(tmp_path.as_posix())
        assert "sample_module.py - This is a sample module." in output

    def test_python_module_without_docstring(self, tmp_path: Path):
        """Test that Python modules without docstrings are listed without description."""
        # Setup
        module_path = tmp_path / "no_docstring.py"
        module_path.write_text('x = 42\n\ndef foo():\n    pass')

        # Test
        output = list_dir(tmp_path.as_posix())
        assert "no_docstring.py" in output
        assert " - " not in output  # No docstring means no description

    def test_package_with_docstring_at_top(self, tmp_path: Path):
        """Test that the current package's docstring is shown at the top."""
        # Setup - create a package
        (tmp_path / "__init__.py").write_text('"""This is my package."""\n\nfrom .module import *')
        (tmp_path / "module.py").write_text('"""A module."""\n\nx = 42')

        # Test
        output = list_dir(tmp_path.as_posix())
        lines = output.split('\n')

        # Package info should be at the top
        assert "This is my package." in lines[0]

        # Module should be listed with its docstring
        assert any("module.py - A module." in line for line in lines)

    def test_nested_package_with_docstring(self, tmp_path: Path):
        """Test that nested packages show their docstrings."""
        # Setup
        subpackage = tmp_path / "subpkg"
        subpackage.mkdir()
        (subpackage / "__init__.py").write_text('"""Subpackage docstring."""')
        (tmp_path / "file.txt").write_text("content")

        # Test
        output = list_dir(tmp_path.as_posix())
        assert "subpkg/ - Subpackage docstring." in output

    def test_custom_ignore_list(self, tmp_path: Path):
        """Test that custom ignore patterns work."""
        # Setup
        (tmp_path / "keep_this").mkdir()
        (tmp_path / "ignore_this").mkdir()
        (tmp_path / "file.txt").write_text("content")

        # Test with custom ignore list
        output = list_dir(tmp_path.as_posix(), ignore=["ignore_this"])
        assert "keep_this/" in output
        assert "ignore_this" not in output
        assert "file.txt" in output

    def test_empty_directory(self, tmp_path: Path):
        """Test listing an empty directory."""
        # Create empty directory
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        # Test
        output = list_dir(empty_dir.as_posix())
        assert output == ""

    def test_directory_without_package(self, tmp_path: Path):
        """Test that directories without __init__.py don't show package info."""
        # Setup - just regular directory
        (tmp_path / "module.py").write_text('"""A module."""\n\nx = 42')
        (tmp_path / "subdir").mkdir()

        # Test
        output = list_dir(tmp_path.as_posix())

        # Should not have "Package:" at the top
        assert not output.startswith("Package:")
        assert "module.py - A module." in output
        assert "subdir/" in output

    def test_mixed_content(self, tmp_path: Path):
        """Test directory with mixed content types."""
        # Setup
        (tmp_path / "script.py").write_text('"""Script file."""\n\nprint("hello")')
        (tmp_path / "data.txt").write_text("some data")
        (tmp_path / "docs").mkdir()
        (tmp_path / ".gitignore").write_text("*.pyc")

        pkg = tmp_path / "package"
        pkg.mkdir()
        (pkg / "__init__.py").write_text('"""A package."""')

        # Test without hidden files
        output = list_dir(tmp_path.as_posix(), show_hidden=False)
        assert "script.py - Script file." in output
        assert "data.txt" in output
        assert "docs/" in output
        assert ".gitignore" not in output  # Hidden file excluded
        assert "package/ - A package." in output