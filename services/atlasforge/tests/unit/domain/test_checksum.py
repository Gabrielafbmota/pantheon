"""Tests for Checksum value object."""

import pytest

from atlasforge.domain.exceptions.validation import ValidationException
from atlasforge.domain.value_objects.checksum import Checksum


class TestChecksum:
    """Test Checksum value object."""

    def test_valid_checksum(self):
        """Test creating valid checksums."""
        # Valid SHA256 checksum (64 hex chars)
        valid_checksum = "a" * 64
        assert Checksum(valid_checksum).value == valid_checksum

        # Another valid checksum
        checksum = "0123456789abcdef" * 4  # 64 chars
        assert Checksum(checksum).value == checksum

    def test_invalid_checksum_too_short(self):
        """Test that checksums shorter than 64 chars are rejected."""
        with pytest.raises(ValidationException, match="Invalid checksum"):
            Checksum("a" * 63)

    def test_invalid_checksum_too_long(self):
        """Test that checksums longer than 64 chars are rejected."""
        with pytest.raises(ValidationException, match="Invalid checksum"):
            Checksum("a" * 65)

    def test_invalid_checksum_uppercase(self):
        """Test that uppercase hex chars are rejected (must be lowercase)."""
        with pytest.raises(ValidationException, match="Invalid checksum"):
            Checksum("A" * 64)

    def test_invalid_checksum_non_hex(self):
        """Test that non-hex characters are rejected."""
        invalid = "g" * 64  # 'g' is not a hex character
        with pytest.raises(ValidationException, match="Invalid checksum"):
            Checksum(invalid)

        invalid = "x" * 64
        with pytest.raises(ValidationException, match="Invalid checksum"):
            Checksum(invalid)

    def test_checksum_equality(self):
        """Test equality comparison."""
        c1 = Checksum("a" * 64)
        c2 = Checksum("a" * 64)
        c3 = Checksum("b" * 64)

        assert c1 == c2
        assert c1 != c3
        assert c1 != ("a" * 64)  # Not equal to string

    def test_checksum_hash(self):
        """Test hashability."""
        c1 = Checksum("a" * 64)
        c2 = Checksum("a" * 64)
        c3 = Checksum("b" * 64)

        assert hash(c1) == hash(c2)
        assert hash(c1) != hash(c3)

        # Can use in set
        checksum_set = {c1, c2, c3}
        assert len(checksum_set) == 2

    def test_checksum_str(self):
        """Test string representation."""
        checksum = "a" * 64
        assert str(Checksum(checksum)) == checksum

    def test_short_form(self):
        """Test short form for display."""
        checksum = Checksum("0123456789abcdef" * 4)
        assert checksum.short_form() == "01234567"  # Default 8 chars
        assert checksum.short_form(12) == "0123456789ab"
        assert checksum.short_form(4) == "0123"

    def test_is_valid_classmethod(self):
        """Test is_valid class method."""
        assert Checksum.is_valid("a" * 64) is True
        assert Checksum.is_valid("0123456789abcdef" * 4) is True
        assert Checksum.is_valid("a" * 63) is False
        assert Checksum.is_valid("A" * 64) is False
        assert Checksum.is_valid("g" * 64) is False
