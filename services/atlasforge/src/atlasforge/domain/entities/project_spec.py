"""ProjectSpec Entity - Immutable specification for project generation."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict

from atlasforge.domain.value_objects.module_name import ModuleName
from atlasforge.domain.value_objects.project_name import ProjectName
from atlasforge.domain.value_objects.template_version import TemplateVersion


@dataclass(frozen=True)
class ProjectSpec:
    """
    Immutable specification for project generation.

    This is the input that drives the entire generation process.
    Same ProjectSpec should always produce the same output (idempotency).

    The frozen dataclass ensures immutability - any modifications create new instances.
    """

    project_name: ProjectName
    template_version: TemplateVersion
    modules: frozenset[ModuleName]
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def has_module(self, module_name: str) -> bool:
        """Check if a specific module is enabled."""
        try:
            return ModuleName(module_name) in self.modules
        except Exception:
            return False

    def with_module(self, module_name: str) -> "ProjectSpec":
        """
        Return new ProjectSpec with added module (immutable operation).

        Since this is a frozen dataclass, we can't modify in place.
        Instead, we create a new instance with the module added.
        """
        new_modules = set(self.modules)
        new_modules.add(ModuleName(module_name))

        return ProjectSpec(
            project_name=self.project_name,
            template_version=self.template_version,
            modules=frozenset(new_modules),
            correlation_id=self.correlation_id,
            created_at=self.created_at,
            metadata=self.metadata.copy(),
        )

    def without_module(self, module_name: str) -> "ProjectSpec":
        """Return new ProjectSpec with removed module (immutable operation)."""
        new_modules = set(self.modules)
        try:
            new_modules.discard(ModuleName(module_name))
        except Exception:
            pass  # Module doesn't exist, no-op

        return ProjectSpec(
            project_name=self.project_name,
            template_version=self.template_version,
            modules=frozenset(new_modules),
            correlation_id=self.correlation_id,
            created_at=self.created_at,
            metadata=self.metadata.copy(),
        )

    def module_list(self) -> list[str]:
        """Get list of module names as strings (sorted for determinism)."""
        return sorted(str(m) for m in self.modules)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "project_name": str(self.project_name),
            "template_version": str(self.template_version),
            "modules": self.module_list(),
            "correlation_id": self.correlation_id,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectSpec":
        """Create ProjectSpec from dictionary."""
        return cls(
            project_name=ProjectName(data["project_name"]),
            template_version=TemplateVersion(data["template_version"]),
            modules=frozenset(ModuleName(m) for m in data.get("modules", [])),
            correlation_id=data.get("correlation_id", str(uuid.uuid4())),
            created_at=datetime.fromisoformat(data["created_at"])
            if "created_at" in data
            else datetime.utcnow(),
            metadata=data.get("metadata", {}),
        )
