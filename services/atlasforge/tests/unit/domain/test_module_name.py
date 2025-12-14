"""Tests for ModuleName value object."""

import pytest

from atlasforge.domain.exceptions.validation import ValidationException
from atlasforge.domain.value_objects.module_name import ModuleName


class TestModuleName:
    """Test ModuleName value object."""

    def test_valid_module_name(self):
        """Test creating valid module names."""
        # Valid names
        assert ModuleName("mongo").value == "mongo"
        assert ModuleName("otel").value == "otel"
        assert ModuleName("events").value == "events"
        assert ModuleName("auth").value == "auth"
        assert ModuleName("jobs").value == "jobs"
        assert ModuleName("my_module").value == "my_module"
        assert ModuleName("module123").value == "module123"

    def test_invalid_module_name_uppercase(self):
        """Test that uppercase names are rejected."""
        with pytest.raises(ValidationException, match="Invalid module name"):
            ModuleName("Mongo")

    def test_invalid_module_name_starts_with_number(self):
        """Test that names starting with numbers are rejected."""
        with pytest.raises(ValidationException, match="Invalid module name"):
            ModuleName("123module")

    def test_invalid_module_name_special_chars(self):
        """Test that special characters are rejected."""
        with pytest.raises(ValidationException, match="Invalid module name"):
            ModuleName("my-module")

        with pytest.raises(ValidationException, match="Invalid module name"):
            ModuleName("my.module")

        with pytest.raises(ValidationException, match="Invalid module name"):
            ModuleName("my@module")

    def test_invalid_module_name_too_long(self):
        """Test that names longer than 32 chars are rejected."""
        long_name = "a" * 33
        with pytest.raises(ValidationException, match="Invalid module name"):
            ModuleName(long_name)

    def test_module_name_max_length(self):
        """Test that 32 char names are accepted."""
        max_name = "a" * 32
        assert ModuleName(max_name).value == max_name

    def test_module_name_equality(self):
        """Test that module names are compared correctly."""
        m1 = ModuleName("mongo")
        m2 = ModuleName("mongo")
        m3 = ModuleName("otel")

        assert m1 == m2
        assert m1 != m3
        assert m1 != "mongo"  # Not equal to string

    def test_module_name_hash(self):
        """Test that module names are hashable (for use in sets)."""
        m1 = ModuleName("mongo")
        m2 = ModuleName("mongo")
        m3 = ModuleName("otel")

        assert hash(m1) == hash(m2)
        assert hash(m1) != hash(m3)

        # Can use in set
        module_set = {m1, m2, m3}
        assert len(module_set) == 2  # m1 and m2 are same

    def test_module_name_str(self):
        """Test string representation."""
        assert str(ModuleName("mongo")) == "mongo"

    def test_is_valid_classmethod(self):
        """Test is_valid class method."""
        assert ModuleName.is_valid("mongo") is True
        assert ModuleName.is_valid("my_module") is True
        assert ModuleName.is_valid("Mongo") is False
        assert ModuleName.is_valid("123module") is False
        assert ModuleName.is_valid("my-module") is False
