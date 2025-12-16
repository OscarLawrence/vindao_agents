"""Tests for path resolution utilities."""
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from vindao_agents.utils.path_resolution import resolve_path, resolve_path_with_fallbacks


class TestResolvePath:
    """Test suite for resolve_path function."""

    def test_resolve_path_finds_file_in_first_directory(self):
        """Test that resolve_path finds a file in the first search directory."""
        with TemporaryDirectory() as tmpdir:
            dir1 = Path(tmpdir) / "dir1"
            dir2 = Path(tmpdir) / "dir2"
            dir1.mkdir()
            dir2.mkdir()

            # Create file in first directory
            test_file = dir1 / "test.txt"
            test_file.write_text("content")

            result = resolve_path("test.txt", [dir1, dir2])
            assert result == test_file
            assert result.exists()

    def test_resolve_path_finds_file_in_fallback_directory(self):
        """Test that resolve_path finds a file in a fallback directory."""
        with TemporaryDirectory() as tmpdir:
            dir1 = Path(tmpdir) / "dir1"
            dir2 = Path(tmpdir) / "dir2"
            dir1.mkdir()
            dir2.mkdir()

            # Create file only in second directory
            test_file = dir2 / "test.txt"
            test_file.write_text("content")

            result = resolve_path("test.txt", [dir1, dir2])
            assert result == test_file
            assert result.exists()

    def test_resolve_path_raises_when_file_not_found(self):
        """Test that resolve_path raises FileNotFoundError when file doesn't exist."""
        with TemporaryDirectory() as tmpdir:
            dir1 = Path(tmpdir) / "dir1"
            dir2 = Path(tmpdir) / "dir2"
            dir1.mkdir()
            dir2.mkdir()

            with pytest.raises(FileNotFoundError) as exc_info:
                resolve_path("nonexistent.txt", [dir1, dir2])

            error_message = str(exc_info.value)
            assert "nonexistent.txt" in error_message
            assert str(dir1) in error_message
            assert str(dir2) in error_message

    def test_resolve_path_accepts_string_paths(self):
        """Test that resolve_path accepts string paths as well as Path objects."""
        with TemporaryDirectory() as tmpdir:
            dir1 = Path(tmpdir) / "dir1"
            dir1.mkdir()

            test_file = dir1 / "test.txt"
            test_file.write_text("content")

            # Pass string instead of Path
            result = resolve_path("test.txt", [str(dir1)])
            assert result == test_file
            assert result.exists()

    def test_resolve_path_respects_priority_order(self):
        """Test that resolve_path respects directory priority order."""
        with TemporaryDirectory() as tmpdir:
            dir1 = Path(tmpdir) / "dir1"
            dir2 = Path(tmpdir) / "dir2"
            dir1.mkdir()
            dir2.mkdir()

            # Create file with same name in both directories
            file1 = dir1 / "test.txt"
            file2 = dir2 / "test.txt"
            file1.write_text("first")
            file2.write_text("second")

            # Should find the file in dir1 (first in priority)
            result = resolve_path("test.txt", [dir1, dir2])
            assert result == file1
            assert result.read_text() == "first"

    def test_resolve_path_with_subdirectories(self):
        """Test that resolve_path works with subdirectories in search path."""
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            sub_dir = base_dir / "sub" / "nested"
            sub_dir.mkdir(parents=True)

            test_file = sub_dir / "test.txt"
            test_file.write_text("content")

            result = resolve_path("test.txt", [sub_dir])
            assert result == test_file


class TestResolvePathWithFallbacks:
    """Test suite for resolve_path_with_fallbacks function."""

    def test_finds_first_filename_in_first_directory(self):
        """Test that the first filename in the first directory is preferred."""
        with TemporaryDirectory() as tmpdir:
            dir1 = Path(tmpdir) / "dir1"
            dir2 = Path(tmpdir) / "dir2"
            dir1.mkdir()
            dir2.mkdir()

            # Create first priority file
            file1 = dir1 / "first.txt"
            file1.write_text("first priority")

            # Create other files
            (dir1 / "second.txt").write_text("fallback")
            (dir2 / "first.txt").write_text("other dir")

            result = resolve_path_with_fallbacks(
                ["first.txt", "second.txt"],
                [dir1, dir2]
            )
            assert result == file1
            assert result.read_text() == "first priority"

    def test_finds_fallback_filename_in_same_directory(self):
        """Test that fallback filename is used when first doesn't exist."""
        with TemporaryDirectory() as tmpdir:
            dir1 = Path(tmpdir) / "dir1"
            dir1.mkdir()

            # Only create fallback file
            fallback = dir1 / "fallback.txt"
            fallback.write_text("fallback content")

            result = resolve_path_with_fallbacks(
                ["first.txt", "fallback.txt"],
                [dir1]
            )
            assert result == fallback

    def test_finds_file_in_fallback_directory(self):
        """Test that fallback directory is searched when file not in first."""
        with TemporaryDirectory() as tmpdir:
            dir1 = Path(tmpdir) / "dir1"
            dir2 = Path(tmpdir) / "dir2"
            dir1.mkdir()
            dir2.mkdir()

            # Create file only in second directory
            file2 = dir2 / "test.txt"
            file2.write_text("in dir2")

            result = resolve_path_with_fallbacks(
                ["test.txt"],
                [dir1, dir2]
            )
            assert result == file2

    def test_raises_when_no_files_found(self):
        """Test that FileNotFoundError is raised when no files exist."""
        with TemporaryDirectory() as tmpdir:
            dir1 = Path(tmpdir) / "dir1"
            dir2 = Path(tmpdir) / "dir2"
            dir1.mkdir()
            dir2.mkdir()

            with pytest.raises(FileNotFoundError) as exc_info:
                resolve_path_with_fallbacks(
                    ["first.txt", "second.txt"],
                    [dir1, dir2]
                )

            error_message = str(exc_info.value)
            assert "first.txt" in error_message
            assert "second.txt" in error_message
            assert str(dir1) in error_message
            assert str(dir2) in error_message

    def test_priority_order_filenames_before_directories(self):
        """Test that all filenames are tried in dir1 before checking dir2."""
        with TemporaryDirectory() as tmpdir:
            dir1 = Path(tmpdir) / "dir1"
            dir2 = Path(tmpdir) / "dir2"
            dir1.mkdir()
            dir2.mkdir()

            # Create first.txt in dir2 and second.txt in dir1
            file_dir2_first = dir2 / "first.txt"
            file_dir1_second = dir1 / "second.txt"
            file_dir2_first.write_text("dir2 first")
            file_dir1_second.write_text("dir1 second")

            # Should find first.txt in dir2 before second.txt in dir1
            result = resolve_path_with_fallbacks(
                ["first.txt", "second.txt"],
                [dir1, dir2]
            )
            assert result == file_dir2_first
            assert result.read_text() == "dir2 first"

    def test_accepts_string_paths(self):
        """Test that function accepts string paths."""
        with TemporaryDirectory() as tmpdir:
            dir1 = Path(tmpdir) / "dir1"
            dir1.mkdir()

            test_file = dir1 / "test.txt"
            test_file.write_text("content")

            result = resolve_path_with_fallbacks(
                ["test.txt"],
                [str(dir1)]
            )
            assert result == test_file

    def test_complex_fallback_scenario(self):
        """Test complex scenario with multiple filenames and directories."""
        with TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            system_dir = Path(tmpdir) / "system"
            user_dir.mkdir()
            system_dir.mkdir()

            # Only create default in system directory
            system_default = system_dir / "default.conf"
            system_default.write_text("system default")

            # Simulate looking for model-specific config, then default
            result = resolve_path_with_fallbacks(
                ["gpt-4.conf", "default.conf"],
                [user_dir, system_dir]
            )
            assert result == system_default

    def test_with_empty_filenames_list(self):
        """Test behavior with empty filenames list."""
        with TemporaryDirectory() as tmpdir:
            dir1 = Path(tmpdir) / "dir1"
            dir1.mkdir()

            with pytest.raises(FileNotFoundError):
                resolve_path_with_fallbacks([], [dir1])

    def test_with_empty_directories_list(self):
        """Test behavior with empty directories list."""
        with pytest.raises(FileNotFoundError):
            resolve_path_with_fallbacks(["test.txt"], [])
