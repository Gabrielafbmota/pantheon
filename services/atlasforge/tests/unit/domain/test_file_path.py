"""Tests for FilePath value object."""

from pathlib import Path

import pytest

from atlasforge.domain.exceptions.validation import ValidationException
from atlasforge.domain.value_objects.file_path import FilePath


class TestFilePath:
    """Test FilePath value object."""

    def test_valid_file_path(self):
        """Test creating valid file paths."""
        assert FilePath("src/main.py").value == "src/main.py"
        assert FilePath("README.md").value == "README.md"
        assert FilePath("src/domain/entities/user.py").value == "src/domain/entities/user.py"

    def test_file_path_normalizes_backslashes(self):
        """Test that backslashes are normalized to forward slashes."""
        fp = FilePath(r"src\main.py")
        assert fp.value == "src/main.py"

        fp2 = FilePath(r"src\domain\entities\user.py")
        assert fp2.value == "src/domain/entities/user.py"

    def test_invalid_absolute_path(self):
        """Test that absolute paths are rejected."""
        with pytest.raises(ValidationException, match="must be relative"):
            FilePath("/absolute/path")

        with pytest.raises(ValidationException, match="must be relative"):
            FilePath("/home/user/file.py")

    def test_invalid_parent_directory_reference(self):
        """Test that parent directory references (..) are rejected."""
        with pytest.raises(ValidationException, match="cannot contain parent directory"):
            FilePath("../file.py")

        with pytest.raises(ValidationException, match="cannot contain parent directory"):
            FilePath("src/../main.py")

    def test_invalid_empty_path(self):
        """Test that empty paths are rejected."""
        with pytest.raises(ValidationException, match="cannot be empty"):
            FilePath("")

        with pytest.raises(ValidationException, match="cannot be empty"):
            FilePath(".")

    def test_file_path_equality(self):
        """Test equality comparison."""
        fp1 = FilePath("src/main.py")
        fp2 = FilePath("src/main.py")
        fp3 = FilePath("src/other.py")

        assert fp1 == fp2
        assert fp1 != fp3
        assert fp1 != "src/main.py"

    def test_file_path_hash(self):
        """Test hashability."""
        fp1 = FilePath("src/main.py")
        fp2 = FilePath("src/main.py")
        fp3 = FilePath("src/other.py")

        assert hash(fp1) == hash(fp2)
        assert hash(fp1) != hash(fp3)

        # Can use in set
        path_set = {fp1, fp2, fp3}
        assert len(path_set) == 2

    def test_to_path(self):
        """Test conversion to pathlib.Path."""
        fp = FilePath("src/main.py")
        path = fp.to_path()
        assert isinstance(path, Path)
        assert str(path) == "src/main.py"

    def test_to_path_with_base(self):
        """Test conversion to pathlib.Path with base directory."""
        fp = FilePath("src/main.py")
        base = Path("/home/user/project")
        path = fp.to_path(base)
        assert str(path) == "/home/user/project/src/main.py"

    def test_parent(self):
        """Test getting parent directory."""
        fp = FilePath("src/domain/entities/user.py")
        parent = fp.parent()
        assert parent is not None
        assert parent.value == "src/domain/entities"

        # Parent of parent
        grandparent = parent.parent()
        assert grandparent is not None
        assert grandparent.value == "src/domain"

        # Top-level file has no parent
        fp2 = FilePath("README.md")
        assert fp2.parent() is None

    def test_name(self):
        """Test getting file name."""
        assert FilePath("src/main.py").name() == "main.py"
        assert FilePath("README.md").name() == "README.md"
        assert FilePath("src/domain/entities/user.py").name() == "user.py"

    def test_suffix(self):
        """Test getting file extension."""
        assert FilePath("main.py").suffix() == ".py"
        assert FilePath("README.md").suffix() == ".md"
        assert FilePath("config.yaml").suffix() == ".yaml"
        assert FilePath("Dockerfile").suffix() == ""

    def test_with_suffix(self):
        """Test changing file extension."""
        fp = FilePath("main.py")
        new_fp = fp.with_suffix(".txt")
        assert new_fp.value == "main.txt"

        fp2 = FilePath("src/main.py")
        new_fp2 = fp2.with_suffix(".md")
        assert new_fp2.value == "src/main.md"

    def test_from_path(self):
        """Test creating FilePath from pathlib.Path."""
        path = Path("src/main.py")
        fp = FilePath.from_path(path)
        assert fp.value == "src/main.py"

    def test_from_path_with_base(self):
        """Test creating FilePath from pathlib.Path relative to base."""
        base = Path("/home/user/project")
        path = Path("/home/user/project/src/main.py")
        fp = FilePath.from_path(path, base)
        assert fp.value == "src/main.py"

    def test_from_path_with_base_not_relative_raises(self):
        """Test that from_path raises if path is not relative to base."""
        base = Path("/home/user/project")
        path = Path("/other/path/file.py")

        with pytest.raises(ValidationException, match="not relative to"):
            FilePath.from_path(path, base)

    def test_is_valid_classmethod(self):
        """Test is_valid class method."""
        assert FilePath.is_valid("src/main.py") is True
        assert FilePath.is_valid("README.md") is True
        assert FilePath.is_valid("/absolute/path") is False
        assert FilePath.is_valid("../parent/file.py") is False
        assert FilePath.is_valid("") is False
