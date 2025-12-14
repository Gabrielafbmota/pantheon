"""Module Port - Interface for module operations."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

from atlasforge.domain.entities.module import Module
from atlasforge.domain.value_objects.module_name import ModuleName


class IModulePort(ABC):
    """
    Interface for module loading and management.

    This port defines how modules are loaded and applied to projects.
    """

    @abstractmethod
    def load_module(self, module_name: ModuleName) -> Module:
        """
        Load a module definition.

        Args:
            module_name: Name of the module to load

        Returns:
            Module entity

        Raises:
            ModuleNotFoundException: If module doesn't exist
        """
        pass

    @abstractmethod
    def get_available_modules(self) -> List[ModuleName]:
        """
        Get list of all available modules.

        Returns:
            List of module names
        """
        pass

    @abstractmethod
    def module_exists(self, module_name: ModuleName) -> bool:
        """
        Check if a module exists.

        Args:
            module_name: Name of module to check

        Returns:
            True if module exists
        """
        pass
