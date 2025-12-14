"""Tests for ProjectName value object."""

import pytest

from atlasforge.domain.exceptions.validation import ValidationException
from atlasforge.domain.value_objects.project_name import ProjectName


class TestProjectName:
    """Test ProjectName value object."""

    def test_valid_project_name(self):
        """Test creating valid project names."""
        assert ProjectName("my-service").value == "my-service"
        assert ProjectName("my_service").value == "my_service"
        assert ProjectName("myservice").value == "myservice"
        assert ProjectName("my-api-service").value == "my-api-service"
        assert ProjectName("service123").value == "service123"

    def test_invalid_project_name_too_short(self):
        """Test that names shorter than 3 chars are rejected."""
        with pytest.raises(ValidationException, match="Invalid project name"):
            ProjectName("ab")

    def test_project_name_min_length(self):
        """Test that 3 char names are accepted."""
        assert ProjectName("abc").value == "abc"

    def test_project_name_max_length(self):
        """Test that 63 char names are accepted."""
        max_name = "a" * 63
        assert ProjectName(max_name).value == max_name

    def test_invalid_project_name_too_long(self):
        """Test that names longer than 63 chars are rejected."""
        long_name = "a" * 64
        with pytest.raises(ValidationException, match="Invalid project name"):
            ProjectName(long_name)

    def test_invalid_project_name_uppercase(self):
        """Test that uppercase names are rejected."""
        with pytest.raises(ValidationException, match="Invalid project name"):
            ProjectName("My-Service")

    def test_invalid_project_name_starts_with_number(self):
        """Test that names starting with numbers are rejected."""
        with pytest.raises(ValidationException, match="Invalid project name"):
            ProjectName("123-service")

    def test_invalid_project_name_consecutive_separators(self):
        """Test that consecutive hyphens/underscores are rejected."""
        with pytest.raises(ValidationException, match="consecutive"):
            ProjectName("my--service")

        with pytest.raises(ValidationException, match="consecutive"):
            ProjectName("my__service")

        with pytest.raises(ValidationException, match="consecutive"):
            ProjectName("my-_service")

        with pytest.raises(ValidationException, match="consecutive"):
            ProjectName("my_-service")

    def test_invalid_project_name_ends_with_separator(self):
        """Test that names ending with hyphen/underscore are rejected."""
        with pytest.raises(ValidationException, match="Cannot end with"):
            ProjectName("my-service-")

        with pytest.raises(ValidationException, match="Cannot end with"):
            ProjectName("my-service_")

    def test_to_snake_case(self):
        """Test conversion to snake_case."""
        assert ProjectName("my-service").to_snake_case() == "my_service"
        assert ProjectName("my-api-service").to_snake_case() == "my_api_service"
        assert ProjectName("my_service").to_snake_case() == "my_service"

    def test_to_pascal_case(self):
        """Test conversion to PascalCase."""
        assert ProjectName("my-service").to_pascal_case() == "MyService"
        assert ProjectName("my-api-service").to_pascal_case() == "MyApiService"
        assert ProjectName("my_service").to_pascal_case() == "MyService"
        assert ProjectName("myservice").to_pascal_case() == "Myservice"

    def test_project_name_equality(self):
        """Test equality comparison."""
        p1 = ProjectName("my-service")
        p2 = ProjectName("my-service")
        p3 = ProjectName("other-service")

        assert p1 == p2
        assert p1 != p3
        assert p1 != "my-service"

    def test_project_name_hash(self):
        """Test hashability."""
        p1 = ProjectName("my-service")
        p2 = ProjectName("my-service")
        p3 = ProjectName("other-service")

        assert hash(p1) == hash(p2)
        assert hash(p1) != hash(p3)

        # Can use in set
        project_set = {p1, p2, p3}
        assert len(project_set) == 2

    def test_is_valid_classmethod(self):
        """Test is_valid class method."""
        assert ProjectName.is_valid("my-service") is True
        assert ProjectName.is_valid("my_service") is True
        assert ProjectName.is_valid("My-Service") is False
        assert ProjectName.is_valid("ab") is False  # Too short
        assert ProjectName.is_valid("my--service") is False
        assert ProjectName.is_valid("my-service-") is False
