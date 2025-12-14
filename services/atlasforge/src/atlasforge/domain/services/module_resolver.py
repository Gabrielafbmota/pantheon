"""ModuleResolver - Domain service for resolving module dependencies."""

from collections import defaultdict, deque
from typing import Dict, List, Set

from atlasforge.domain.entities.module import Module
from atlasforge.domain.exceptions.validation import ValidationException
from atlasforge.domain.ports.module_port import IModulePort
from atlasforge.domain.value_objects.module_name import ModuleName


class ModuleResolver:
    """
    Domain service for resolving module dependencies.

    Uses topological sorting (Kahn's algorithm) to ensure modules are
    applied in the correct order based on their dependencies.
    """

    def __init__(self, module_port: IModulePort):
        """
        Initialize module resolver.

        Args:
            module_port: Port for loading modules
        """
        self.module_port = module_port

    def resolve(self, requested_modules: frozenset[ModuleName]) -> List[Module]:
        """
        Resolve dependencies and return ordered list of modules.

        Uses topological sort to ensure dependencies are applied first.
        Detects circular dependencies and raises exception.

        Args:
            requested_modules: Set of modules requested by user

        Returns:
            List of modules in dependency order (dependencies first)

        Raises:
            ValidationException: If circular dependency detected or module not found
        """
        # Load all modules and their dependencies
        modules: Dict[ModuleName, Module] = {}
        to_process: deque[ModuleName] = deque(requested_modules)
        processed: Set[ModuleName] = set()

        while to_process:
            module_name = to_process.popleft()

            if module_name in processed:
                continue

            # Load module
            if not self.module_port.module_exists(module_name):
                raise ValidationException(f"Module '{module_name}' not found")

            module = self.module_port.load_module(module_name)
            modules[module_name] = module
            processed.add(module_name)

            # Add dependencies to queue (only required dependencies)
            for dep in module.get_required_dependencies():
                if dep not in processed:
                    to_process.append(dep)

        # Perform topological sort
        return self._topological_sort(modules)

    def _topological_sort(self, modules: Dict[ModuleName, Module]) -> List[Module]:
        """
        Sort modules by dependencies using Kahn's algorithm.

        Args:
            modules: Dictionary of module name -> Module

        Returns:
            List of modules in dependency order

        Raises:
            ValidationException: If circular dependency detected
        """
        # Calculate in-degree for each module
        in_degree: Dict[ModuleName, int] = {name: 0 for name in modules}

        # Build adjacency list and calculate in-degrees
        adjacency: Dict[ModuleName, List[ModuleName]] = defaultdict(list)

        for module in modules.values():
            for dep in module.get_required_dependencies():
                if dep in in_degree:  # Only count dependencies that are being installed
                    adjacency[dep].append(module.name)
                    in_degree[module.name] += 1

        # Queue of modules with no dependencies
        queue: deque[ModuleName] = deque(
            [name for name, degree in in_degree.items() if degree == 0]
        )

        result: List[Module] = []

        while queue:
            current = queue.popleft()
            result.append(modules[current])

            # Reduce in-degree for dependent modules
            for dependent in adjacency[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # Check if all modules were processed (detect cycles)
        if len(result) != len(modules):
            # Find modules involved in cycle
            unprocessed = [name for name, degree in in_degree.items() if degree > 0]
            raise ValidationException(
                f"Circular dependency detected among modules: {', '.join(str(m) for m in unprocessed)}"
            )

        return result

    def validate_dependencies(self, modules: List[ModuleName]) -> bool:
        """
        Validate that all dependencies are available.

        Args:
            modules: List of module names to validate

        Returns:
            True if all dependencies can be satisfied

        Raises:
            ValidationException: If any dependency is missing
        """
        for module_name in modules:
            if not self.module_port.module_exists(module_name):
                raise ValidationException(f"Module '{module_name}' not found")

            module = self.module_port.load_module(module_name)

            # Check required dependencies
            for dep in module.get_required_dependencies():
                if not self.module_port.module_exists(dep):
                    raise ValidationException(
                        f"Module '{module_name}' requires '{dep}' which is not available"
                    )

        return True

    def get_dependency_tree(self, module_name: ModuleName, depth: int = 0) -> Dict:
        """
        Get dependency tree for a module (for visualization/debugging).

        Args:
            module_name: Module to get tree for
            depth: Current recursion depth (for cycle detection)

        Returns:
            Dictionary representing dependency tree
        """
        if depth > 10:  # Prevent infinite recursion
            return {"error": "Maximum depth exceeded (possible cycle)"}

        if not self.module_port.module_exists(module_name):
            return {"error": f"Module '{module_name}' not found"}

        module = self.module_port.load_module(module_name)

        tree = {
            "name": str(module.name),
            "version": str(module.version),
            "description": module.description,
            "dependencies": [],
        }

        for dep in module.get_all_dependencies():
            tree["dependencies"].append(self.get_dependency_tree(dep, depth + 1))

        return tree
