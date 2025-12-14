"""Tests for TemplateVersion value object."""

import pytest

from atlasforge.domain.exceptions.validation import ValidationException
from atlasforge.domain.value_objects.template_version import TemplateVersion


class TestTemplateVersion:
    """Test TemplateVersion value object."""

    def test_valid_template_version(self):
        """Test creating valid template versions."""
        assert TemplateVersion("1.0.0").value == "1.0.0"
        assert TemplateVersion("0.0.1").value == "0.0.1"
        assert TemplateVersion("10.20.30").value == "10.20.30"
        assert TemplateVersion("999.999.999").value == "999.999.999"

    def test_invalid_template_version_format(self):
        """Test that invalid formats are rejected."""
        with pytest.raises(ValidationException, match="Invalid template version"):
            TemplateVersion("1.0")  # Missing patch

        with pytest.raises(ValidationException, match="Invalid template version"):
            TemplateVersion("1")  # Missing minor and patch

        with pytest.raises(ValidationException, match="Invalid template version"):
            TemplateVersion("v1.0.0")  # 'v' prefix not allowed

        with pytest.raises(ValidationException, match="Invalid template version"):
            TemplateVersion("1.0.0-beta")  # Pre-release suffix not allowed

    def test_version_properties(self):
        """Test major, minor, patch properties."""
        v = TemplateVersion("1.2.3")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3

        v2 = TemplateVersion("10.20.30")
        assert v2.major == 10
        assert v2.minor == 20
        assert v2.patch == 30

    def test_version_comparison_equal(self):
        """Test equality comparison."""
        v1 = TemplateVersion("1.0.0")
        v2 = TemplateVersion("1.0.0")
        v3 = TemplateVersion("1.0.1")

        assert v1 == v2
        assert v1 != v3

    def test_version_comparison_less_than(self):
        """Test less than comparison."""
        assert TemplateVersion("1.0.0") < TemplateVersion("1.0.1")
        assert TemplateVersion("1.0.0") < TemplateVersion("1.1.0")
        assert TemplateVersion("1.0.0") < TemplateVersion("2.0.0")
        assert TemplateVersion("0.9.9") < TemplateVersion("1.0.0")

    def test_version_comparison_greater_than(self):
        """Test greater than comparison."""
        assert TemplateVersion("1.0.1") > TemplateVersion("1.0.0")
        assert TemplateVersion("1.1.0") > TemplateVersion("1.0.9")
        assert TemplateVersion("2.0.0") > TemplateVersion("1.9.9")

    def test_version_comparison_less_equal(self):
        """Test less than or equal comparison."""
        assert TemplateVersion("1.0.0") <= TemplateVersion("1.0.0")
        assert TemplateVersion("1.0.0") <= TemplateVersion("1.0.1")
        assert not (TemplateVersion("1.0.1") <= TemplateVersion("1.0.0"))

    def test_version_comparison_greater_equal(self):
        """Test greater than or equal comparison."""
        assert TemplateVersion("1.0.0") >= TemplateVersion("1.0.0")
        assert TemplateVersion("1.0.1") >= TemplateVersion("1.0.0")
        assert not (TemplateVersion("1.0.0") >= TemplateVersion("1.0.1"))

    def test_is_breaking_change(self):
        """Test breaking change detection."""
        v1 = TemplateVersion("1.0.0")
        v2 = TemplateVersion("2.0.0")
        v3 = TemplateVersion("1.5.0")
        v4 = TemplateVersion("1.0.1")

        assert v1.is_breaking_change(v2) is True  # Major bump
        assert v1.is_breaking_change(v3) is False  # Minor bump
        assert v1.is_breaking_change(v4) is False  # Patch bump

    def test_version_hash(self):
        """Test hashability."""
        v1 = TemplateVersion("1.0.0")
        v2 = TemplateVersion("1.0.0")
        v3 = TemplateVersion("1.0.1")

        assert hash(v1) == hash(v2)
        assert hash(v1) != hash(v3)

        # Can use in set
        version_set = {v1, v2, v3}
        assert len(version_set) == 2

    def test_version_str(self):
        """Test string representation."""
        assert str(TemplateVersion("1.2.3")) == "1.2.3"

    def test_is_valid_classmethod(self):
        """Test is_valid class method."""
        assert TemplateVersion.is_valid("1.0.0") is True
        assert TemplateVersion.is_valid("10.20.30") is True
        assert TemplateVersion.is_valid("1.0") is False
        assert TemplateVersion.is_valid("v1.0.0") is False
        assert TemplateVersion.is_valid("1.0.0-beta") is False
