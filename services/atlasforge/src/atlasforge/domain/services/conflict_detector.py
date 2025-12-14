"""ConflictDetector - Domain service for detecting file modifications."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List

from atlasforge.domain.entities.template_manifest import TemplateManifest
from atlasforge.domain.ports.checksum_port import IChecksumPort
from atlasforge.domain.ports.filesystem_port import IFileSystemPort


class ConflictType(Enum):
    """Type of conflict detected."""

    MODIFIED = "modified"  # File was modified by user
    DELETED = "deleted"  # File was deleted by user
    ADDED = "added"  # File was added by user (not managed)


@dataclass
class ConflictInfo:
    """Information about a detected conflict."""

    path: str
    type: ConflictType
    message: str
    is_editable: bool = False  # If file is marked as user-editable


class ConflictDetector:
    """
    Domain service for detecting conflicts between user changes and template updates.

    This service compares the current state of files with the manifest checksums
    to identify files that have been modified by users.
    """

    def __init__(self, filesystem: IFileSystemPort, checksum: IChecksumPort):
        """
        Initialize conflict detector.

        Args:
            filesystem: Filesystem port for reading files
            checksum: Checksum port for calculating checksums
        """
        self.filesystem = filesystem
        self.checksum = checksum

    def detect_conflicts(
        self, manifest: TemplateManifest, project_path: Path
    ) -> List[ConflictInfo]:
        """
        Compare current files with manifest checksums.

        Detects:
        - Files that have been modified by users (checksum mismatch)
        - Files that have been deleted by users
        - Files that have been added by users (not in manifest)

        Args:
            manifest: Template manifest with tracked files
            project_path: Root path of the project

        Returns:
            List of detected conflicts
        """
        conflicts = []

        # Check managed files for modifications/deletions
        for file_path, managed_file in manifest.managed_files.items():
            full_path = project_path / file_path

            if not self.filesystem.exists(full_path):
                # File was deleted by user
                conflicts.append(
                    ConflictInfo(
                        path=file_path,
                        type=ConflictType.DELETED,
                        message=f"File {file_path} was deleted by user",
                        is_editable=managed_file.is_user_editable,
                    )
                )
                continue

            # Calculate current checksum
            current_content = self.filesystem.read_file(full_path)
            current_checksum = self.checksum.calculate(current_content)

            if current_checksum != managed_file.checksum:
                # File was modified by user
                conflicts.append(
                    ConflictInfo(
                        path=file_path,
                        type=ConflictType.MODIFIED,
                        message=f"File {file_path} was modified by user",
                        is_editable=managed_file.is_user_editable,
                    )
                )

        return conflicts

    def has_conflicts(self, manifest: TemplateManifest, project_path: Path) -> bool:
        """
        Quick check if there are any conflicts.

        Args:
            manifest: Template manifest
            project_path: Root path of the project

        Returns:
            True if any conflicts exist
        """
        return len(self.detect_conflicts(manifest, project_path)) > 0

    def filter_critical_conflicts(self, conflicts: List[ConflictInfo]) -> List[ConflictInfo]:
        """
        Filter conflicts to only critical ones (non-editable files).

        User-editable files (like domain/ or application/) being modified
        is expected and not critical. Infrastructure files being modified is critical.

        Args:
            conflicts: List of all conflicts

        Returns:
            List of critical conflicts only
        """
        return [c for c in conflicts if not c.is_editable]

    def get_modified_files(self, conflicts: List[ConflictInfo]) -> List[str]:
        """Get list of modified file paths."""
        return [c.path for c in conflicts if c.type == ConflictType.MODIFIED]

    def get_deleted_files(self, conflicts: List[ConflictInfo]) -> List[str]:
        """Get list of deleted file paths."""
        return [c.path for c in conflicts if c.type == ConflictType.DELETED]

    def get_conflict_summary(self, conflicts: List[ConflictInfo]) -> dict[str, int]:
        """
        Get summary statistics of conflicts.

        Returns:
            Dictionary with conflict counts by type
        """
        return {
            "total": len(conflicts),
            "modified": len([c for c in conflicts if c.type == ConflictType.MODIFIED]),
            "deleted": len([c for c in conflicts if c.type == ConflictType.DELETED]),
            "critical": len(self.filter_critical_conflicts(conflicts)),
        }
