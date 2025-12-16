"""Tests for read_file and read_files."""

# stdlib
from pathlib import Path

# third party
import pytest

# local
from vindao_agents.tools.file_ops.read_file import read_file
from vindao_agents.tools.file_ops.read_files import read_files


class TestReadFile:

    def test_read_existing_file(self, tmp_path):
        """Test reading an existing file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        result = read_file(str(test_file))
        assert result == "Hello, World!"

    def test_read_nonexistent_file_raises_error(self):
        """Test that reading a nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            read_file("/nonexistent/file.txt")


class TestReadFiles:

    def test_read_multiple_files(self, tmp_path):
        """Test reading multiple existing files."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("Content 1")
        file2.write_text("Content 2")

        result = read_files(str(file1), str(file2))

        assert f"# {file1}" in result
        assert "Content 1" in result
        assert f"# {file2}" in result
        assert "Content 2" in result

    def test_read_single_file(self, tmp_path):
        """Test reading a single file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        result = read_files(str(test_file))

        assert f"# {test_file}" in result
        assert "Test content" in result

    def test_error_handling_formats_exception(self, tmp_path):
        """Test that errors are properly formatted (Issue #2)."""
        result = read_files("/nonexistent/file.txt")

        # Should contain formatted exception, not object repr
        assert "FileNotFoundError" in result
        assert "/nonexistent/file.txt" in result
        assert "Traceback" in result
        # Should NOT contain object repr like <FileNotFoundError object at 0x...>
        assert "<FileNotFoundError object" not in result

    def test_mixed_valid_and_invalid_files(self, tmp_path):
        """Test reading mix of valid and invalid files."""
        valid_file = tmp_path / "valid.txt"
        valid_file.write_text("Valid content")

        result = read_files(str(valid_file), "/nonexistent/file.txt")

        # Should contain valid file content
        assert "Valid content" in result
        # Should contain formatted error for invalid file
        assert "FileNotFoundError" in result
        assert "/nonexistent/file.txt" in result

    def test_empty_file(self, tmp_path):
        """Test reading an empty file."""
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("")

        result = read_files(str(empty_file))

        assert f"# {empty_file}" in result
        # Content should be empty but header should be present
        assert result.strip() == f"# {empty_file}"
