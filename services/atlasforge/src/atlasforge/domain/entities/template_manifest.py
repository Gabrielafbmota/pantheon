"""TemplateManifest Entity - Tracks generated project state for upgrades."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from atlasforge.domain.value_objects.checksum import Checksum
from atlasforge.domain.value_objects.file_path import FilePath
from atlasforge.domain.value_objects.module_name import ModuleName
from atlasforge.domain.value_objects.template_version import TemplateVersion


@dataclass
class ManagedFile:
    """
    Represents a file managed by AtlasForge.

    These files can be tracked for modifications and upgraded safely.
    """

    path: FilePath
    checksum: Checksum
    source: str  # 'base' | 'module:<name>' | 'integration:<name>'
    is_user_editable: bool = False

    def __post_init__(self) -> None:
        """Ensure types are correct."""
        if not isinstance(self.path, FilePath):
            object.__setattr__(self, "path", FilePath(str(self.path)))
        if not isinstance(self.checksum, Checksum):
            object.__setattr__(self, "checksum", Checksum(str(self.checksum)))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": str(self.path),
            "checksum": str(self.checksum),
            "source": self.source,
            "is_user_editable": self.is_user_editable,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ManagedFile":
        """Create from dictionary."""
        return cls(
            path=FilePath(data["path"]),
            checksum=Checksum(data["checksum"]),
            source=data["source"],
            is_user_editable=data.get("is_user_editable", False),
        )


@dataclass
class TemplateManifest:
    """
    Manifest that tracks what AtlasForge generated.

    Stored in .atlasforge/manifest.json in generated projects.

    Used for:
    - Upgrade tracking (what changed between versions?)
    - Conflict detection (did user modify a managed file?)
    - Module tracking (what modules are enabled?)
    - Audit trail (when was project generated/upgraded?)
    """

    template_name: str
    template_version: TemplateVersion
    project_name: str
    modules_enabled: List[ModuleName]
    managed_files: Dict[str, ManagedFile]  # path -> ManagedFile
    generated_at: datetime
    correlation_id: str
    last_upgraded_at: Optional[datetime] = None
    upgrade_history: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Ensure correct types."""
        if not isinstance(self.template_version, TemplateVersion):
            object.__setattr__(
                self, "template_version", TemplateVersion(str(self.template_version))
            )

        # Convert module strings to ModuleName objects if needed
        if self.modules_enabled and not isinstance(self.modules_enabled[0], ModuleName):
            object.__setattr__(
                self,
                "modules_enabled",
                [ModuleName(str(m)) for m in self.modules_enabled],
            )

    def get_file(self, path: str) -> Optional[ManagedFile]:
        """Get managed file by path."""
        return self.managed_files.get(path)

    def is_file_modified(self, path: str, current_checksum: Checksum) -> bool:
        """
        Check if a managed file has been modified by the user.

        Compares current checksum with the one stored in manifest.
        """
        managed = self.get_file(path)
        if not managed:
            return False  # Not managed, can't be "modified" in our tracking sense
        return managed.checksum != current_checksum

    def add_module(self, module: ModuleName) -> None:
        """Mark module as enabled."""
        if module not in self.modules_enabled:
            self.modules_enabled.append(module)

    def remove_module(self, module: ModuleName) -> None:
        """Mark module as disabled."""
        if module in self.modules_enabled:
            self.modules_enabled.remove(module)

    def has_module(self, module_name: str) -> bool:
        """Check if module is enabled."""
        try:
            return ModuleName(module_name) in self.modules_enabled
        except Exception:
            return False

    def record_upgrade(self, new_version: TemplateVersion, correlation_id: str) -> None:
        """
        Record an upgrade operation in the manifest.

        This maintains an audit trail of all upgrades.
        """
        self.upgrade_history.append(
            {
                "from_version": str(self.template_version),
                "to_version": str(new_version),
                "upgraded_at": datetime.utcnow().isoformat(),
                "correlation_id": correlation_id,
            }
        )
        object.__setattr__(self, "template_version", new_version)
        object.__setattr__(self, "last_upgraded_at", datetime.utcnow())

    def add_managed_file(self, file: ManagedFile) -> None:
        """Add a file to the managed files tracking."""
        self.managed_files[str(file.path)] = file

    def remove_managed_file(self, path: str) -> None:
        """Remove a file from managed files tracking."""
        if path in self.managed_files:
            del self.managed_files[path]

    def get_files_by_source(self, source: str) -> List[ManagedFile]:
        """Get all files from a specific source (e.g., 'base', 'module:mongo')."""
        return [f for f in self.managed_files.values() if f.source == source]

    def get_user_editable_files(self) -> List[ManagedFile]:
        """Get all files marked as user-editable."""
        return [f for f in self.managed_files.values() if f.is_user_editable]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "template_name": self.template_name,
            "template_version": str(self.template_version),
            "project_name": self.project_name,
            "modules_enabled": [str(m) for m in self.modules_enabled],
            "managed_files": {
                path: file.to_dict() for path, file in self.managed_files.items()
            },
            "generated_at": self.generated_at.isoformat(),
            "correlation_id": self.correlation_id,
            "last_upgraded_at": self.last_upgraded_at.isoformat()
            if self.last_upgraded_at
            else None,
            "upgrade_history": self.upgrade_history,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemplateManifest":
        """Create manifest from dictionary (JSON deserialization)."""
        return cls(
            template_name=data["template_name"],
            template_version=TemplateVersion(data["template_version"]),
            project_name=data["project_name"],
            modules_enabled=[ModuleName(m) for m in data.get("modules_enabled", [])],
            managed_files={
                path: ManagedFile.from_dict(file_data)
                for path, file_data in data.get("managed_files", {}).items()
            },
            generated_at=datetime.fromisoformat(data["generated_at"]),
            correlation_id=data["correlation_id"],
            last_upgraded_at=datetime.fromisoformat(data["last_upgraded_at"])
            if data.get("last_upgraded_at")
            else None,
            upgrade_history=data.get("upgrade_history", []),
        )
