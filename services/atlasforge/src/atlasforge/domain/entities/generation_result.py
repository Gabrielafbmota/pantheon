"""GenerationResult Entity - Captures generation outcome."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from atlasforge.domain.entities.template_manifest import TemplateManifest


@dataclass
class GenerationResult:
    """
    Result of a project generation or upgrade.

    Used for auditing and integration with Mnemosyne.
    Provides complete information about what was generated and any issues.
    """

    success: bool
    project_path: Path
    manifest: TemplateManifest
    files_created: List[str] = field(default_factory=list)
    files_updated: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    correlation_id: str = ""
    duration_seconds: float = 0.0
    completed_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_files(self) -> int:
        """Total files affected."""
        return len(self.files_created) + len(self.files_updated)

    @property
    def has_errors(self) -> bool:
        """Check if there were any errors."""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if there were any warnings."""
        return len(self.warnings) > 0

    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        self.success = False

    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "project_path": str(self.project_path),
            "files_created": self.files_created,
            "files_updated": self.files_updated,
            "errors": self.errors,
            "warnings": self.warnings,
            "correlation_id": self.correlation_id,
            "duration_seconds": self.duration_seconds,
            "completed_at": self.completed_at.isoformat(),
            "total_files": self.total_files,
        }
