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


class TestParseDocstringFromFile:
    """Tests for parse_docstring_from_file function."""

    def test_file_with_single_line_docstring(self, tmp_path: Path):
        """Test parsing a file with a single-line docstring."""
        file_path = tmp_path / "module.py"
        file_path.write_text('"""This is a single line docstring."""\n\ndef foo():\n    pass')

        result = parse_docstring_from_file(file_path)
        assert result == "This is a single line docstring."

    def test_file_with_multiline_docstring(self, tmp_path: Path):
        """Test parsing a file with a multi-line docstring."""
        file_path = tmp_path / "module.py"
        file_path.write_text(
            '"""This is a multi-line docstring.\n\n'
            'It has multiple paragraphs.\n'
            '"""\n\n'
            'def foo():\n'
            '    pass'
        )

        result = parse_docstring_from_file(file_path)
        assert result == "This is a multi-line docstring.\n\nIt has multiple paragraphs."

    def test_file_without_docstring(self, tmp_path: Path):
        """Test parsing a file without a docstring."""
        file_path = tmp_path / "module.py"
        file_path.write_text('x = 42\n\ndef foo():\n    pass')

        result = parse_docstring_from_file(file_path)
        assert result is None

    def test_file_with_only_comments(self, tmp_path: Path):
        """Test parsing a file with only comments (no docstring)."""
        file_path = tmp_path / "module.py"
        file_path.write_text('# This is a comment\n# Not a docstring\n\nx = 42')

        result = parse_docstring_from_file(file_path)
        assert result is None

    def test_file_with_syntax_error(self, tmp_path: Path):
        """Test parsing a file with syntax errors returns None."""
        file_path = tmp_path / "broken.py"
        file_path.write_text('"""Docstring."""\n\ndef foo(\n    # syntax error - unclosed paren')

        result = parse_docstring_from_file(file_path)
        assert result is None

    def test_nonexistent_file(self, tmp_path: Path):
        """Test parsing a non-existent file returns None."""
        file_path = tmp_path / "does_not_exist.py"

        result = parse_docstring_from_file(file_path)
        assert result is None

    def test_file_with_relative_imports(self, tmp_path: Path):
        """Test parsing a file with relative imports (should not execute)."""
        file_path = tmp_path / "module.py"
        file_path.write_text(
            '"""Module with relative imports."""\n\n'
            'from .nonexistent import something\n'
        )

        # Should successfully extract docstring without executing the imports
        result = parse_docstring_from_file(file_path)
        assert result == "Module with relative imports."

    def test_empty_file(self, tmp_path: Path):
        """Test parsing an empty file returns None."""
        file_path = tmp_path / "empty.py"
        file_path.write_text('')

        result = parse_docstring_from_file(file_path)
        assert result is None

    def test_file_with_single_quote_docstring(self, tmp_path: Path):
        """Test parsing a file with single-quoted docstring."""
        file_path = tmp_path / "module.py"
        file_path.write_text("'''Single quoted docstring.'''\n\nx = 42")

        result = parse_docstring_from_file(file_path)
        assert result == "Single quoted docstring."
