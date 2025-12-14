"""Manifest Repository Port - Interface for manifest persistence."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from atlasforge.domain.entities.template_manifest import TemplateManifest


class IManifestRepositoryPort(ABC):
    """
    Interface for template manifest persistence.

    This port defines how manifests are saved and loaded.
    Implementations can use JSON files, databases, or any other storage.
    """

    @abstractmethod
    def save(self, manifest: TemplateManifest, project_path: Path) -> None:
        """
        Save manifest to project.

        Typically saves to .atlasforge/manifest.json in the project.

        Args:
            manifest: Manifest to save
            project_path: Root path of the project
        """
        pass

    @abstractmethod
    def load(self, project_path: Path) -> Optional[TemplateManifest]:
        """
        Load manifest from project.

        Typically loads from .atlasforge/manifest.json in the project.

        Args:
            project_path: Root path of the project

        Returns:
            Loaded manifest or None if not found
        """
        pass

    @abstractmethod
    def exists(self, project_path: Path) -> bool:
        """
        Check if a manifest exists in the project.

        Args:
            project_path: Root path of the project

        Returns:
            True if manifest exists
        """
        pass

    @abstractmethod
    def delete(self, project_path: Path) -> None:
        """
        Delete manifest from project.

        Args:
            project_path: Root path of the project
        """
        pass
