"""FilePath value object."""

from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from atlasforge.domain.exceptions.validation import ValidationException


@dataclass(frozen=True)
class FilePath:
    """
    Value object for file path.

    Stores paths in POSIX format (forward slashes) for cross-platform consistency.
    Validates that path is relative (not absolute) for portability.
    """

    value: str

    def __post_init__(self) -> None:
        # Validate not absolute
        posix_path = PurePosixPath(self.value)
        if posix_path.is_absolute():
            raise ValidationException(
                f"FilePath must be relative, not absolute: {self.value}"
            )

        # Validate no parent directory references for security
        if ".." in self.value:
            raise ValidationException(
                f"FilePath cannot contain parent directory references (..): {self.value}"
            )

        # Validate not empty
        if not self.value or self.value == ".":
            raise ValidationException("FilePath cannot be empty or current directory (.)")

        # Normalize to forward slashes
        normalized = self.value.replace("\\", "/")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FilePath):
            return self.value == other.value
        return False

    def to_path(self, base: Path | None = None) -> Path:
        """Convert to pathlib.Path, optionally joined with base directory."""
        path = Path(self.value)
        if base:
            return base / path
        return path

    def parent(self) -> "FilePath | None":
        """Get parent directory path."""
        posix_path = PurePosixPath(self.value)
        parent = posix_path.parent
        if str(parent) == ".":
            return None
        return FilePath(str(parent))

    def name(self) -> str:
        """Get file name (last component of path)."""
        return PurePosixPath(self.value).name

    def suffix(self) -> str:
        """Get file extension including the dot (e.g., '.py')."""
        return PurePosixPath(self.value).suffix

    def with_suffix(self, suffix: str) -> "FilePath":
        """Return new FilePath with different suffix."""
        posix_path = PurePosixPath(self.value)
        return FilePath(str(posix_path.with_suffix(suffix)))

    @classmethod
    def from_path(cls, path: Path, base: Path | None = None) -> "FilePath":
        """Create FilePath from pathlib.Path, optionally relative to base."""
        if base:
            try:
                rel_path = path.relative_to(base)
            except ValueError as e:
                raise ValidationException(f"Path {path} is not relative to {base}") from e
        else:
            rel_path = path

        # Convert to POSIX format (forward slashes)
        posix_str = rel_path.as_posix()
        return cls(posix_str)

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if a value is a valid file path without raising exception."""
        try:
            cls(value)
            return True
        except ValidationException:
            return False
