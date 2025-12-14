"""Module Entity - Represents a modular capability."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from atlasforge.domain.value_objects.module_name import ModuleName
from atlasforge.domain.value_objects.template_version import TemplateVersion


@dataclass(frozen=True)
class ModuleDependency:
    """Represents a dependency on another module."""

    module_name: ModuleName
    is_optional: bool = False

    def __str__(self) -> str:
        optional_marker = " (optional)" if self.is_optional else ""
        return f"{self.module_name}{optional_marker}"


@dataclass(frozen=True)
class Module:
    """
    Represents a modular capability (e.g., mongo, otel, events).

    Modules inject code, dependencies, and configuration into projects.
    They are immutable and can depend on other modules.
    """

    name: ModuleName
    version: TemplateVersion
    description: str
    dependencies: frozenset[ModuleDependency] = field(default_factory=frozenset)
    poetry_dependencies: Dict[str, str] = field(default_factory=dict)
    template_path: Optional[Path] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def requires_module(self, module_name: str) -> bool:
        """
        Check if this module requires another module (non-optional dependency).

        Args:
            module_name: Name of the module to check

        Returns:
            True if module is a required dependency
        """
        try:
            target = ModuleName(module_name)
            return any(
                dep.module_name == target and not dep.is_optional for dep in self.dependencies
            )
        except Exception:
            return False

    def has_dependency(self, module_name: str, include_optional: bool = True) -> bool:
        """
        Check if this module has a dependency (required or optional).

        Args:
            module_name: Name of the module to check
            include_optional: If True, include optional dependencies

        Returns:
            True if module is a dependency
        """
        try:
            target = ModuleName(module_name)
            return any(
                dep.module_name == target and (include_optional or not dep.is_optional)
                for dep in self.dependencies
            )
        except Exception:
            return False

    def get_all_dependencies(self) -> list[ModuleName]:
        """
        Get all dependencies (including transitive - to be resolved by service).

        Returns:
            List of module names that this module depends on
        """
        return [dep.module_name for dep in self.dependencies]

    def get_required_dependencies(self) -> list[ModuleName]:
        """
        Get only required (non-optional) dependencies.

        Returns:
            List of required module names
        """
        return [dep.module_name for dep in self.dependencies if not dep.is_optional]

    def get_optional_dependencies(self) -> list[ModuleName]:
        """
        Get only optional dependencies.

        Returns:
            List of optional module names
        """
        return [dep.module_name for dep in self.dependencies if dep.is_optional]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": str(self.name),
            "version": str(self.version),
            "description": self.description,
            "dependencies": [
                {"module": str(dep.module_name), "optional": dep.is_optional}
                for dep in self.dependencies
            ],
            "poetry_dependencies": self.poetry_dependencies,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Module":
        """Create Module from dictionary."""
        dependencies = []
        for dep_data in data.get("dependencies", []):
            dependencies.append(
                ModuleDependency(
                    module_name=ModuleName(dep_data["module"]),
                    is_optional=dep_data.get("optional", False),
                )
            )

        return cls(
            name=ModuleName(data["name"]),
            version=TemplateVersion(data["version"]),
            description=data["description"],
            dependencies=frozenset(dependencies),
            poetry_dependencies=data.get("poetry_dependencies", {}),
            template_path=Path(data["template_path"]) if "template_path" in data else None,
            metadata=data.get("metadata", {}),
        )
