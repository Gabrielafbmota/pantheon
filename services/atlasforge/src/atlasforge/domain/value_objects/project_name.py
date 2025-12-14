"""ProjectName value object."""

import re
from dataclasses import dataclass

from atlasforge.domain.exceptions.validation import ValidationException


@dataclass(frozen=True)
class ProjectName:
    """
    Value object for project name.

    Enforces naming conventions: lowercase, alphanumeric + hyphens/underscores, 3-63 chars.
    Compatible with filesystem, Docker, and domain names.
    """

    value: str

    # Pattern: lowercase, starts with letter, alphanumeric + hyphen/underscore, 3-63 chars
    PATTERN = re.compile(r"^[a-z][a-z0-9_-]{2,62}$")

    def __post_init__(self) -> None:
        if not self.PATTERN.match(self.value):
            raise ValidationException(
                f"Invalid project name '{self.value}'. "
                f"Must be lowercase, start with a letter, contain only alphanumeric characters, "
                f"hyphens, or underscores, and be between 3-63 characters long."
            )

        # Additional validation: no consecutive hyphens/underscores
        if "--" in self.value or "__" in self.value or "-_" in self.value or "_-" in self.value:
            raise ValidationException(
                f"Invalid project name '{self.value}'. "
                f"Cannot contain consecutive hyphens or underscores."
            )

        # Must not end with hyphen or underscore
        if self.value.endswith("-") or self.value.endswith("_"):
            raise ValidationException(
                f"Invalid project name '{self.value}'. "
                f"Cannot end with a hyphen or underscore."
            )

    def __str__(self) -> str:
        return self.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ProjectName):
            return self.value == other.value
        return False

    def to_snake_case(self) -> str:
        """Convert to snake_case (for Python module names)."""
        return self.value.replace("-", "_")

    def to_pascal_case(self) -> str:
        """Convert to PascalCase (for class names)."""
        parts = self.value.replace("_", "-").split("-")
        return "".join(word.capitalize() for word in parts)

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if a value is a valid project name without raising exception."""
        if not cls.PATTERN.match(value):
            return False
        if "--" in value or "__" in value or "-_" in value or "_-" in value:
            return False
        if value.endswith("-") or value.endswith("_"):
            return False
        return True
