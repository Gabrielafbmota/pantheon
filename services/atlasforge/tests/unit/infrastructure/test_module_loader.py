"""Tests for ModuleLoaderAdapter."""

import pytest
from pathlib import Path

from atlasforge.domain.value_objects.module_name import ModuleName
from atlasforge.infrastructure.modules.module_loader import (
    ModuleLoaderAdapter,
    ModuleLoadException,
)


class TestModuleLoaderAdapter:
    """Test ModuleLoaderAdapter."""

    @pytest.fixture
    def modules_dir(self, tmp_path: Path) -> Path:
        """Create a temporary modules directory."""
        modules_dir = tmp_path / "modules"
        modules_dir.mkdir()
        return modules_dir

    @pytest.fixture
    def sample_module_yaml(self) -> str:
        """Sample module.yaml content."""
        return """
name: mongo
version: 1.0.0
description: MongoDB adapter
category: database
dependencies: []
files:
  - source: infrastructure/database/mongo_client.py.j2
    destination: src/{{project_name|snake_case}}/infrastructure/database/mongo_client.py
    is_user_editable: true
pip_dependencies:
  - motor>=3.3.0
  - pymongo>=4.6.0
environment_variables:
  - name: MONGO_URI
    description: MongoDB connection string
    required: true
"""

    @pytest.fixture
    def mongo_module(self, modules_dir: Path, sample_module_yaml: str) -> Path:
        """Create a sample mongo module."""
        mongo_dir = modules_dir / "mongo"
        mongo_dir.mkdir()

        # Create module.yaml
        (mongo_dir / "module.yaml").write_text(sample_module_yaml)

        # Create files directory
        (mongo_dir / "files" / "infrastructure" / "database").mkdir(parents=True)
        (mongo_dir / "files" / "infrastructure" / "database" / "mongo_client.py.j2").write_text(
            "# MongoDB client"
        )

        return mongo_dir

    def test_load_module_success(self, modules_dir: Path, mongo_module: Path):
        """Test loading a module successfully."""
        loader = ModuleLoaderAdapter(modules_dir)

        module = loader.load_module(ModuleName("mongo"))

        assert module.name == ModuleName("mongo")
        assert module.version == "1.0.0"
        assert module.description == "MongoDB adapter"
        assert len(module.files) == 1
        assert len(module.pip_dependencies) == 2
        assert "motor>=3.3.0" in module.pip_dependencies

    def test_load_module_not_found(self, modules_dir: Path):
        """Test loading a non-existent module."""
        loader = ModuleLoaderAdapter(modules_dir)

        with pytest.raises(ModuleLoadException, match="Module 'nonexistent' not found"):
            loader.load_module(ModuleName("nonexistent"))

    def test_load_module_caching(self, modules_dir: Path, mongo_module: Path):
        """Test that modules are cached after first load."""
        loader = ModuleLoaderAdapter(modules_dir)

        # Load once
        module1 = loader.load_module(ModuleName("mongo"))

        # Load again (should come from cache)
        module2 = loader.load_module(ModuleName("mongo"))

        # Should be the same instance
        assert module1 is module2

    def test_load_modules_multiple(self, modules_dir: Path, mongo_module: Path):
        """Test loading multiple modules."""
        # Create another module
        otel_dir = modules_dir / "otel"
        otel_dir.mkdir()
        (otel_dir / "module.yaml").write_text(
            """
name: otel
version: 1.0.0
description: OpenTelemetry
category: observability
dependencies: []
files: []
pip_dependencies: []
environment_variables: []
"""
        )

        loader = ModuleLoaderAdapter(modules_dir)

        modules = loader.load_modules(
            frozenset([ModuleName("mongo"), ModuleName("otel")])
        )

        assert len(modules) == 2
        module_names = {m.name.value for m in modules}
        assert module_names == {"mongo", "otel"}

    def test_list_available_modules(self, modules_dir: Path, mongo_module: Path):
        """Test listing available modules."""
        # Create another module
        otel_dir = modules_dir / "otel"
        otel_dir.mkdir()
        (otel_dir / "module.yaml").write_text("name: otel\nversion: 1.0.0")

        loader = ModuleLoaderAdapter(modules_dir)

        available = loader.list_available_modules()

        assert sorted(available) == ["mongo", "otel"]

    def test_list_available_modules_empty(self, modules_dir: Path):
        """Test listing when no modules exist."""
        loader = ModuleLoaderAdapter(modules_dir)

        available = loader.list_available_modules()

        assert available == []

    def test_load_module_with_dependencies(self, modules_dir: Path):
        """Test loading a module with dependencies."""
        # Create base module
        base_dir = modules_dir / "base"
        base_dir.mkdir()
        (base_dir / "module.yaml").write_text(
            """
name: base
version: 1.0.0
description: Base module
dependencies: []
files: []
pip_dependencies: []
environment_variables: []
"""
        )

        # Create module with dependency
        derived_dir = modules_dir / "derived"
        derived_dir.mkdir()
        (derived_dir / "module.yaml").write_text(
            """
name: derived
version: 1.0.0
description: Derived module
dependencies:
  - base
files: []
pip_dependencies: []
environment_variables: []
"""
        )

        loader = ModuleLoaderAdapter(modules_dir)

        module = loader.load_module(ModuleName("derived"))

        assert module.name == ModuleName("derived")
        assert len(module.dependencies) == 1
        assert ModuleName("base") in module.dependencies

    def test_load_module_invalid_yaml(self, modules_dir: Path):
        """Test loading a module with invalid YAML."""
        invalid_dir = modules_dir / "invalid"
        invalid_dir.mkdir()
        (invalid_dir / "module.yaml").write_text("invalid: yaml: content:")

        loader = ModuleLoaderAdapter(modules_dir)

        with pytest.raises(ModuleLoadException):
            loader.load_module(ModuleName("invalid"))

    def test_module_file_configuration(self, modules_dir: Path, mongo_module: Path):
        """Test that module files are parsed correctly."""
        loader = ModuleLoaderAdapter(modules_dir)

        module = loader.load_module(ModuleName("mongo"))

        assert len(module.files) == 1
        file = list(module.files)[0]

        assert file.source == "infrastructure/database/mongo_client.py.j2"
        assert (
            file.destination
            == "src/{{project_name|snake_case}}/infrastructure/database/mongo_client.py"
        )
        assert file.is_user_editable is True
