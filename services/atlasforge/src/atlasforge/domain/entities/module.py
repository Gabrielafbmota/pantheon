"""Module Entity - Represents a modular capability."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from atlasforge.domain.value_objects.module_name import ModuleName
from atlasforge.domain.value_objects.template_version import TemplateVersion


@dataclass(frozen=True)
class ModuleFile:
    """Represents a file within a module."""

    source: str  # Source file path relative to module files/ directory
    destination: str  # Destination path (may contain template variables)
    is_user_editable: bool = True  # Whether users are expected to edit this file

    def __hash__(self) -> int:
        """Make ModuleFile hashable for use in frozensets."""
        return hash((self.source, self.destination, self.is_user_editable))


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
    version: str  # Using str instead of TemplateVersion for simplicity
    description: str
    files: frozenset[ModuleFile] = field(default_factory=frozenset)
    dependencies: frozenset[ModuleName] = field(default_factory=frozenset)
    pip_dependencies: tuple[str, ...] = field(default_factory=tuple)
    environment_variables: tuple[tuple, ...] = field(default_factory=tuple)
    template_path: Optional[Path] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self) -> int:
        """Custom hash to allow use in sets even with metadata present."""
        return hash(
            (
                self.name,
                self.version,
                self.description,
                tuple(self.files),
                tuple(self.dependencies),
                self.pip_dependencies,
                self.environment_variables,
            )
        )

    def has_dependency(self, module_name: str) -> bool:
        """
        Check if this module has a dependency.

        Args:
            module_name: Name of the module to check

        Returns:
            True if module is a dependency
        """
        try:
            target = ModuleName(module_name)
            return target in self.dependencies
        except Exception:
            return False

    def get_all_dependencies(self) -> list[ModuleName]:
        """
        Get all dependencies.

        Returns:
            List of module names that this module depends on
        """
        return list(self.dependencies)

    def get_required_dependencies(self) -> list[ModuleName]:
        """Alias kept for compatibility with older resolver."""
        return self.get_all_dependencies()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": str(self.name),
            "version": self.version,
            "description": self.description,
            "files": [
                {
                    "source": f.source,
                    "destination": f.destination,
                    "is_user_editable": f.is_user_editable,
                }
                for f in self.files
            ],
            "dependencies": [str(dep) for dep in self.dependencies],
            "pip_dependencies": list(self.pip_dependencies),
            "environment_variables": [dict(ev) if isinstance(ev, tuple) else ev for ev in self.environment_variables],
            "metadata": self.metadata,
        }
