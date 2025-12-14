"""JSON manifest repository implementation."""

import json
from pathlib import Path
from typing import Optional

from atlasforge.domain.entities.template_manifest import TemplateManifest
from atlasforge.domain.ports.filesystem_port import IFileSystemPort
from atlasforge.domain.ports.manifest_repository_port import IManifestRepositoryPort


class JSONManifestRepository(IManifestRepositoryPort):
    """
    JSON file-based manifest repository.

    Stores manifests in .atlasforge/manifest.json within projects.
    """

    MANIFEST_DIR = ".atlasforge"
    MANIFEST_FILE = "manifest.json"

    def __init__(self, filesystem: IFileSystemPort):
        """
        Initialize repository.

        Args:
            filesystem: Filesystem port for file operations
        """
        self.filesystem = filesystem

    def _get_manifest_path(self, project_path: Path) -> Path:
        """Get full path to manifest file."""
        return project_path / self.MANIFEST_DIR / self.MANIFEST_FILE

    def save(self, manifest: TemplateManifest, project_path: Path) -> None:
        """
        Save manifest to project.

        Creates .atlasforge directory if it doesn't exist.

        Args:
            manifest: Manifest to save
            project_path: Root path of the project
        """
        manifest_path = self._get_manifest_path(project_path)

        # Ensure .atlasforge directory exists
        self.filesystem.create_dir(manifest_path.parent)

        # Convert manifest to JSON
        manifest_dict = manifest.to_dict()
        json_content = json.dumps(manifest_dict, indent=2, ensure_ascii=False)

        # Write to file
        self.filesystem.write_file(manifest_path, json_content)

    def load(self, project_path: Path) -> Optional[TemplateManifest]:
        """
        Load manifest from project.

        Args:
            project_path: Root path of the project

        Returns:
            Loaded manifest or None if not found
        """
        manifest_path = self._get_manifest_path(project_path)

        if not self.filesystem.exists(manifest_path):
            return None

        # Read JSON content
        json_content = self.filesystem.read_file(manifest_path)

        # Parse JSON
        try:
            manifest_dict = json.loads(json_content)
            return TemplateManifest.from_dict(manifest_dict)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Manifest is corrupted or invalid format
            raise ValueError(f"Invalid manifest format: {e}") from e

    def exists(self, project_path: Path) -> bool:
        """
        Check if a manifest exists in the project.

        Args:
            project_path: Root path of the project

        Returns:
            True if manifest exists
        """
        manifest_path = self._get_manifest_path(project_path)
        return self.filesystem.exists(manifest_path)

    def delete(self, project_path: Path) -> None:
        """
        Delete manifest from project.

        Args:
            project_path: Root path of the project
        """
        manifest_path = self._get_manifest_path(project_path)
        if self.filesystem.exists(manifest_path):
            self.filesystem.delete_file(manifest_path)
