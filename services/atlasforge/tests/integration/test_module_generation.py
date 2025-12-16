"""Integration tests for module-based project generation."""

import pytest
from pathlib import Path

from atlasforge.application.use_cases.generate_project import GenerateProjectUseCase
from atlasforge.domain.entities.project_spec import ProjectSpec
from atlasforge.domain.value_objects.module_name import ModuleName
from atlasforge.domain.value_objects.project_name import ProjectName
from atlasforge.domain.value_objects.template_version import TemplateVersion
from atlasforge.infrastructure.checksum.sha256_checksum import SHA256ChecksumAdapter
from atlasforge.infrastructure.filesystem.local_filesystem_adapter import (
    LocalFileSystemAdapter,
)
from atlasforge.infrastructure.modules.module_loader import ModuleLoaderAdapter
from atlasforge.infrastructure.persistence.json_manifest_repository import (
    JSONManifestRepository,
)
from atlasforge.infrastructure.templating.jinja2_engine import Jinja2TemplateEngine


class TestModuleGeneration:
    """Test project generation with modules."""

    @pytest.fixture
    def templates_dir(self) -> Path:
        """Get templates directory."""
        # Assume we're in tests/integration/
        return Path(__file__).parent.parent.parent / "src" / "atlasforge" / "templates"

    @pytest.fixture
    def filesystem(self) -> LocalFileSystemAdapter:
        """Create filesystem adapter."""
        return LocalFileSystemAdapter()

    @pytest.fixture
    def template_engine(self, templates_dir: Path) -> Jinja2TemplateEngine:
        """Create template engine."""
        return Jinja2TemplateEngine(templates_dir)

    @pytest.fixture
    def checksum(self) -> SHA256ChecksumAdapter:
        """Create checksum adapter."""
        return SHA256ChecksumAdapter()

    @pytest.fixture
    def manifest_repo(self, filesystem: LocalFileSystemAdapter) -> JSONManifestRepository:
        """Create manifest repository."""
        return JSONManifestRepository(filesystem)

    @pytest.fixture
    def module_loader(self, templates_dir: Path) -> ModuleLoaderAdapter:
        """Create module loader."""
        modules_dir = templates_dir / "modules"
        return ModuleLoaderAdapter(modules_dir)

    @pytest.fixture
    def use_case(
        self,
        filesystem: LocalFileSystemAdapter,
        template_engine: Jinja2TemplateEngine,
        checksum: SHA256ChecksumAdapter,
        manifest_repo: JSONManifestRepository,
        module_loader: ModuleLoaderAdapter,
    ) -> GenerateProjectUseCase:
        """Create use case with module support."""
        return GenerateProjectUseCase(
            filesystem=filesystem,
            template_engine=template_engine,
            checksum=checksum,
            manifest_repo=manifest_repo,
            module_loader=module_loader,
        )

    def test_generate_project_with_mongo_module(
        self, use_case: GenerateProjectUseCase, tmp_path: Path
    ):
        """Test generating a project with MongoDB module."""
        spec = ProjectSpec(
            project_name=ProjectName("test-mongo-service"),
            template_version=TemplateVersion("1.0.0"),
            modules=frozenset([ModuleName("mongo")]),
        )

        result = use_case.execute(spec, tmp_path)

        assert result.success
        assert result.total_files > 13  # Base files + module files

        # Check that MongoDB files were created
        project_path = tmp_path / "test-mongo-service"
        mongo_client = (
            project_path
            / "src"
            / "test_mongo_service"
            / "infrastructure"
            / "database"
            / "mongo_client.py"
        )
        assert mongo_client.exists()

        # Check database port
        db_port = (
            project_path
            / "src"
            / "test_mongo_service"
            / "domain"
            / "ports"
            / "database_port.py"
        )
        assert db_port.exists()

        # Verify content has project name rendered
        content = mongo_client.read_text()
        assert "test_mongo_service" in content or "test-mongo-service" in content

    def test_generate_project_with_otel_module(
        self, use_case: GenerateProjectUseCase, tmp_path: Path
    ):
        """Test generating a project with OpenTelemetry module."""
        spec = ProjectSpec(
            project_name=ProjectName("test-otel-service"),
            template_version=TemplateVersion("1.0.0"),
            modules=frozenset([ModuleName("otel")]),
        )

        result = use_case.execute(spec, tmp_path)

        assert result.success

        # Check that OTEL files were created
        project_path = tmp_path / "test-otel-service"
        telemetry = (
            project_path
            / "src"
            / "test_otel_service"
            / "infrastructure"
            / "observability"
            / "telemetry.py"
        )
        assert telemetry.exists()

        # Check logging config
        logging_config = (
            project_path
            / "src"
            / "test_otel_service"
            / "infrastructure"
            / "observability"
            / "logging_config.py"
        )
        assert logging_config.exists()

    def test_generate_project_with_events_module(
        self, use_case: GenerateProjectUseCase, tmp_path: Path
    ):
        """Test generating a project with Events module."""
        spec = ProjectSpec(
            project_name=ProjectName("test-events-service"),
            template_version=TemplateVersion("1.0.0"),
            modules=frozenset([ModuleName("events")]),
        )

        result = use_case.execute(spec, tmp_path)

        assert result.success

        # Check that Events files were created
        project_path = tmp_path / "test-events-service"

        base_event = (
            project_path
            / "src"
            / "test_events_service"
            / "domain"
            / "events"
            / "base_event.py"
        )
        assert base_event.exists()

        event_publisher = (
            project_path
            / "src"
            / "test_events_service"
            / "infrastructure"
            / "events"
            / "event_publisher.py"
        )
        assert event_publisher.exists()

        event_port = (
            project_path
            / "src"
            / "test_events_service"
            / "domain"
            / "ports"
            / "event_port.py"
        )
        assert event_port.exists()

    def test_generate_project_with_multiple_modules(
        self, use_case: GenerateProjectUseCase, tmp_path: Path
    ):
        """Test generating a project with multiple modules."""
        spec = ProjectSpec(
            project_name=ProjectName("full-service"),
            template_version=TemplateVersion("1.0.0"),
            modules=frozenset(
                [ModuleName("mongo"), ModuleName("otel"), ModuleName("events")]
            ),
        )

        result = use_case.execute(spec, tmp_path)

        assert result.success
        assert len(result.files_created) > 20  # Base + 3 modules

        project_path = tmp_path / "full-service"

        # Verify all module files exist
        # MongoDB
        assert (
            project_path
            / "src"
            / "full_service"
            / "infrastructure"
            / "database"
            / "mongo_client.py"
        ).exists()

        # OTEL
        assert (
            project_path
            / "src"
            / "full_service"
            / "infrastructure"
            / "observability"
            / "telemetry.py"
        ).exists()

        # Events
        assert (
            project_path / "src" / "full_service" / "domain" / "events" / "base_event.py"
        ).exists()

    def test_manifest_includes_module_files(
        self, use_case: GenerateProjectUseCase, tmp_path: Path, manifest_repo
    ):
        """Test that manifest includes files from modules."""
        spec = ProjectSpec(
            project_name=ProjectName("test-manifest"),
            template_version=TemplateVersion("1.0.0"),
            modules=frozenset([ModuleName("mongo")]),
        )

        result = use_case.execute(spec, tmp_path)

        assert result.success

        # Load manifest
        project_path = tmp_path / "test-manifest"
        manifest = manifest_repo.load(project_path)

        # Check that module files are in manifest
        file_paths = list(manifest.managed_files.keys())

        assert any(
            "infrastructure/database/mongo_client.py" in path for path in file_paths
        )
        assert any("domain/ports/database_port.py" in path for path in file_paths)

    def test_module_files_are_valid_python(
        self, use_case: GenerateProjectUseCase, tmp_path: Path
    ):
        """Test that generated module files are valid Python."""
        spec = ProjectSpec(
            project_name=ProjectName("valid-python"),
            template_version=TemplateVersion("1.0.0"),
            modules=frozenset([ModuleName("mongo"), ModuleName("events")]),
        )

        result = use_case.execute(spec, tmp_path)

        assert result.success

        project_path = tmp_path / "valid-python"

        # Compile all Python files to check syntax
        import py_compile

        python_files = list(project_path.rglob("*.py"))
        assert len(python_files) > 0

        for py_file in python_files:
            try:
                py_compile.compile(str(py_file), doraise=True)
            except py_compile.PyCompileError as e:
                pytest.fail(f"Invalid Python syntax in {py_file}: {e}")
