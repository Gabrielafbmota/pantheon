"""ModuleName value object."""

import re
from dataclasses import dataclass

from atlasforge.domain.exceptions.validation import ValidationException


@dataclass(frozen=True)
class ModuleName:
    """
    Value object for module name.

    Enforces naming conventions: lowercase, alphanumeric + underscore, max 32 chars.
    """

    value: str

    PATTERN = re.compile(r"^[a-z][a-z0-9_]{0,31}$")
    ALLOWED_MODULES = {"mongo", "otel", "events", "auth", "jobs"}

    def __post_init__(self) -> None:
        if not self.PATTERN.match(self.value):
            raise ValidationException(
                f"Invalid module name '{self.value}'. "
                f"Must be lowercase alphanumeric + underscore, max 32 chars, "
                f"starting with a letter."
            )

    def __str__(self) -> str:
        return self.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ModuleName):
            return self.value == other.value
        return False

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if a value is a valid module name without raising exception."""
        return bool(cls.PATTERN.match(value))
