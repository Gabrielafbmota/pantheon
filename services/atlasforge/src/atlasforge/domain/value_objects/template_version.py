"""TemplateVersion value object."""

import re
from dataclasses import dataclass
from typing import Tuple

from atlasforge.domain.exceptions.validation import ValidationException


@dataclass(frozen=True)
class TemplateVersion:
    """
    Value object for template version (semantic versioning).

    Enforces semantic versioning format: MAJOR.MINOR.PATCH
    """

    value: str

    # Semantic versioning pattern: X.Y.Z where X, Y, Z are integers
    PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

    def __post_init__(self) -> None:
        if not self.PATTERN.match(self.value):
            raise ValidationException(
                f"Invalid template version '{self.value}'. "
                f"Must follow semantic versioning: MAJOR.MINOR.PATCH (e.g., 1.0.0)"
            )

    def __str__(self) -> str:
        return self.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TemplateVersion):
            return self.value == other.value
        return False

    def __lt__(self, other: object) -> bool:
        """Compare versions for ordering."""
        if not isinstance(other, TemplateVersion):
            return NotImplemented
        return self._parts() < other._parts()

    def __le__(self, other: object) -> bool:
        if not isinstance(other, TemplateVersion):
            return NotImplemented
        return self._parts() <= other._parts()

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, TemplateVersion):
            return NotImplemented
        return self._parts() > other._parts()

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, TemplateVersion):
            return NotImplemented
        return self._parts() >= other._parts()

    def _parts(self) -> Tuple[int, int, int]:
        """Extract (major, minor, patch) as integers for comparison."""
        match = self.PATTERN.match(self.value)
        if not match:
            raise ValidationException(f"Invalid version format: {self.value}")
        return (int(match.group(1)), int(match.group(2)), int(match.group(3)))

    @property
    def major(self) -> int:
        """Get major version number."""
        return self._parts()[0]

    @property
    def minor(self) -> int:
        """Get minor version number."""
        return self._parts()[1]

    @property
    def patch(self) -> int:
        """Get patch version number."""
        return self._parts()[2]

    def is_breaking_change(self, other: "TemplateVersion") -> bool:
        """Check if upgrading to other version would be a breaking change."""
        return other.major > self.major

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if a value is a valid template version without raising exception."""
        return bool(cls.PATTERN.match(value))
