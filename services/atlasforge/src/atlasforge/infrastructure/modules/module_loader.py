"""Module loader adapter."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, FrozenSet, List

import yaml

from atlasforge.domain.entities.module import Module, ModuleFile
from atlasforge.domain.exceptions.base import AtlasForgeException
from atlasforge.domain.ports.module_port import IModulePort
from atlasforge.domain.value_objects.module_name import ModuleName

logger = logging.getLogger(__name__)


@dataclass
class ModuleConfig:
    """Module configuration loaded from YAML."""

    name: str
    version: str
    description: str
    category: str
    dependencies: List[str]
    files: List[Dict[str, str]]
    pip_dependencies: List[str]
    environment_variables: List[Dict[str, str]]
    configuration: Dict[str, any]


class ModuleLoadException(AtlasForgeException):
    """Exception raised when module loading fails."""

    pass


class ModuleLoaderAdapter(IModulePort):
    """
    Adapter for loading modules from filesystem.

    Implements IModulePort interface.
    """

    def __init__(self, modules_dir: Path) -> None:
        """
        Initialize module loader.

        Args:
            modules_dir: Directory containing module definitions
        """
        self.modules_dir = modules_dir
        self._cache: Dict[str, Module] = {}

    def load_module(self, module_name: ModuleName) -> Module:
        """
        Load a module by name.

        Args:
            module_name: Name of the module to load

        Returns:
            Module instance

        Raises:
            ModuleLoadException: If module cannot be loaded
        """
        # Check cache
        if module_name.value in self._cache:
            logger.debug(f"Module '{module_name}' loaded from cache")
            return self._cache[module_name.value]

        # Load from filesystem
        module_path = self.modules_dir / module_name.value / "module.yaml"

        if not module_path.exists():
            raise ModuleLoadException(
                f"Module '{module_name}' not found at {module_path}"
            )

        try:
            with open(module_path, "r") as f:
                config_data = yaml.safe_load(f)

            module = self._parse_module_config(config_data, module_path.parent)

            # Cache it
            self._cache[module_name.value] = module

            logger.info(
                f"Module '{module_name}' loaded successfully",
                extra={
                    "module_name": module_name.value,
                    "version": module.version,
                    "files": len(module.files),
                },
            )

            return module

        except Exception as e:
            raise ModuleLoadException(
                f"Failed to load module '{module_name}': {e}"
            ) from e

    def load_modules(self, module_names: FrozenSet[ModuleName]) -> FrozenSet[Module]:
        """
        Load multiple modules.

        Args:
            module_names: Set of module names to load

        Returns:
            Set of loaded modules
        """
        modules = set()
        for module_name in module_names:
            module = self.load_module(module_name)
            modules.add(module)

        return frozenset(modules)

    def list_available_modules(self) -> List[str]:
        """
        List all available modules.

        Returns:
            List of module names
        """
        if not self.modules_dir.exists():
            return []

        modules = []
        for item in self.modules_dir.iterdir():
            if item.is_dir() and (item / "module.yaml").exists():
                modules.append(item.name)

        return sorted(modules)

    def get_available_modules(self) -> List[ModuleName]:
        """
        Get list of all available modules.

        Returns:
            List of module names
        """
        return [ModuleName(name) for name in self.list_available_modules()]

    def module_exists(self, module_name: ModuleName) -> bool:
        """
        Check if a module exists.

        Args:
            module_name: Name of module to check

        Returns:
            True if module exists
        """
        module_path = self.modules_dir / module_name.value / "module.yaml"
        return module_path.exists()

    def _parse_module_config(self, config_data: Dict, module_dir: Path) -> Module:
        """
        Parse module configuration YAML.

        Args:
            config_data: Raw YAML data
            module_dir: Module directory path

        Returns:
            Module instance
        """
        # Parse module files
        module_files = []
        for file_config in config_data.get("files", []):
            module_file = ModuleFile(
                source=file_config["source"],
                destination=file_config["destination"],
                is_user_editable=file_config.get("is_user_editable", True),
            )
            module_files.append(module_file)

        # Parse dependencies
        dependencies = frozenset(
            ModuleName(dep) for dep in config_data.get("dependencies", [])
        )

        env_vars = tuple(
            tuple(sorted(ev.items())) if isinstance(ev, dict) else (ev,) for ev in config_data.get("environment_variables", [])
        )

        return Module(
            name=ModuleName(config_data["name"]),
            version=config_data["version"],
            description=config_data.get("description", ""),
            files=frozenset(module_files),
            dependencies=dependencies,
            pip_dependencies=tuple(config_data.get("pip_dependencies", [])),
            environment_variables=env_vars,
        )
