"""Checksum value object."""

import re
from dataclasses import dataclass

from atlasforge.domain.exceptions.validation import ValidationException


@dataclass(frozen=True)
class Checksum:
    """
    Value object for file checksum (SHA256 hex digest).

    Enforces that checksum is a valid 64-character hexadecimal string.
    """

    value: str

    # SHA256 produces 64 hexadecimal characters
    PATTERN = re.compile(r"^[a-f0-9]{64}$")

    def __post_init__(self) -> None:
        if not self.PATTERN.match(self.value):
            raise ValidationException(
                f"Invalid checksum '{self.value}'. "
                f"Must be a 64-character hexadecimal string (SHA256 digest)."
            )

    def __str__(self) -> str:
        return self.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Checksum):
            return self.value == other.value
        return False

    def short_form(self, length: int = 8) -> str:
        """Return shortened form of checksum for display purposes."""
        return self.value[:length]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if a value is a valid checksum without raising exception."""
        return bool(cls.PATTERN.match(value))
