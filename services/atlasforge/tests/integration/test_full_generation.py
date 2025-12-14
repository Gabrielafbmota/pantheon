"""Integration tests for full project generation."""

from pathlib import Path

import pytest

from atlasforge.application.use_cases.generate_project import GenerateProjectUseCase
from atlasforge.domain.entities.project_spec import ProjectSpec
from atlasforge.domain.value_objects.module_name import ModuleName
from atlasforge.domain.value_objects.project_name import ProjectName
from atlasforge.domain.value_objects.template_version import TemplateVersion
from atlasforge.infrastructure.checksum.sha256_checksum import SHA256ChecksumAdapter
from atlasforge.infrastructure.filesystem.local_filesystem_adapter import (
    LocalFileSystemAdapter,
)
from atlasforge.infrastructure.persistence.json_manifest_repository import (
    JSONManifestRepository,
)
from atlasforge.infrastructure.templating.jinja2_engine import Jinja2TemplateEngine


@pytest.fixture
def filesystem():
    """Provide filesystem adapter."""
    return LocalFileSystemAdapter()


@pytest.fixture
def checksum():
    """Provide checksum adapter."""
    return SHA256ChecksumAdapter()


@pytest.fixture
def templates_dir():
    """Get templates directory path."""
    # Navigate from tests/ to src/atlasforge/templates/
    test_dir = Path(__file__).parent.parent.parent
    return test_dir / "src" / "atlasforge" / "templates"


@pytest.fixture
def template_engine(templates_dir):
    """Provide template engine."""
    return Jinja2TemplateEngine(templates_dir)


@pytest.fixture
def manifest_repo(filesystem):
    """Provide manifest repository."""
    return JSONManifestRepository(filesystem)


@pytest.fixture
def generate_use_case(filesystem, template_engine, checksum, manifest_repo):
    """Provide GenerateProjectUseCase."""
    return GenerateProjectUseCase(
        filesystem=filesystem,
        template_engine=template_engine,
        checksum=checksum,
        manifest_repo=manifest_repo,
    )


class TestFullProjectGeneration:
    """Test complete project generation flow."""

    def test_generate_basic_project(self, generate_use_case, tmp_path):
        """Test generating a basic project without modules."""
        # Create spec
        spec = ProjectSpec(
            project_name=ProjectName("test-service"),
            template_version=TemplateVersion("1.0.0"),
            modules=frozenset(),
        )

        # Generate project
        result = generate_use_case.execute(spec, tmp_path)

        # Verify result
        assert result.success is True
        assert result.has_errors is False
        assert result.total_files > 0

        # Verify project structure
        project_path = tmp_path / "test-service"
        assert project_path.exists()

        # Verify key files exist
        assert (project_path / "pyproject.toml").exists()
        assert (project_path / "README.md").exists()
        assert (project_path / "Dockerfile").exists()
        assert (project_path / ".gitignore").exists()

        # Verify Clean Architecture structure
        assert (project_path / "src" / "test_service" / "domain").exists()
        assert (project_path / "src" / "test_service" / "application").exists()
        assert (project_path / "src" / "test_service" / "infrastructure").exists()
        assert (project_path / "src" / "test_service" / "presentation").exists()

        # Verify API files
        assert (
            project_path / "src" / "test_service" / "presentation" / "api" / "main.py"
        ).exists()

        # Verify tests
        assert (project_path / "tests" / "conftest.py").exists()
        assert (project_path / "tests" / "test_api.py").exists()

        # Verify manifest
        assert (project_path / ".atlasforge" / "manifest.json").exists()

    def test_generated_project_name_conversion(self, generate_use_case, tmp_path):
        """Test that project names are converted correctly in templates."""
        spec = ProjectSpec(
            project_name=ProjectName("my-api-service"),
            template_version=TemplateVersion("1.0.0"),
            modules=frozenset(),
        )

        result = generate_use_case.execute(spec, tmp_path)
        assert result.success is True

        project_path = tmp_path / "my-api-service"

        # Should use snake_case for Python packages
        assert (project_path / "src" / "my_api_service").exists()

        # Check pyproject.toml has correct name
        pyproject = (project_path / "pyproject.toml").read_text()
        assert 'name = "my-api-service"' in pyproject
        assert 'include = "my_api_service"' in pyproject

        # Check README has PascalCase title
        readme = (project_path / "README.md").read_text()
        assert "# MyApiService" in readme

    def test_manifest_contains_all_files(self, generate_use_case, manifest_repo, tmp_path):
        """Test that manifest tracks all generated files."""
        spec = ProjectSpec(
            project_name=ProjectName("test-service"),
            template_version=TemplateVersion("1.0.0"),
            modules=frozenset(),
        )

        result = generate_use_case.execute(spec, tmp_path)
        project_path = tmp_path / "test-service"

        # Load manifest
        manifest = manifest_repo.load(project_path)
        assert manifest is not None

        # Verify manifest metadata
        assert manifest.template_name == "atlas-base"
        assert str(manifest.template_version) == "1.0.0"
        assert manifest.project_name == "test-service"

        # Verify files are tracked
        assert len(manifest.managed_files) > 0

        # Verify key files are tracked
        tracked_paths = list(manifest.managed_files.keys())
        assert "pyproject.toml" in tracked_paths
        assert "README.md" in tracked_paths

        # Verify checksums are present
        for managed_file in manifest.managed_files.values():
            assert managed_file.checksum is not None
            assert len(str(managed_file.checksum)) == 64  # SHA256

    def test_manifest_marks_user_editable_files(
        self, generate_use_case, manifest_repo, tmp_path
    ):
        """Test that manifest correctly marks user-editable files."""
        spec = ProjectSpec(
            project_name=ProjectName("test-service"),
            template_version=TemplateVersion("1.0.0"),
            modules=frozenset(),
        )

        generate_use_case.execute(spec, tmp_path)
        project_path = tmp_path / "test-service"

        manifest = manifest_repo.load(project_path)

        # Config files should NOT be editable
        pyproject_file = manifest.get_file("pyproject.toml")
        assert pyproject_file is not None
        assert pyproject_file.is_user_editable is False

        # README should be editable
        readme_file = manifest.get_file("README.md")
        assert readme_file is not None
        assert readme_file.is_user_editable is True

        # Test files should be editable
        test_files = [f for f in manifest.managed_files.values() if "tests/" in str(f.path)]
        for test_file in test_files:
            assert test_file.is_user_editable is True

    def test_cannot_generate_if_project_exists(self, generate_use_case, tmp_path):
        """Test that generation fails if project already exists."""
        spec = ProjectSpec(
            project_name=ProjectName("test-service"),
            template_version=TemplateVersion("1.0.0"),
            modules=frozenset(),
        )

        # First generation succeeds
        result1 = generate_use_case.execute(spec, tmp_path)
        assert result1.success is True

        # Second generation should fail
        from atlasforge.domain.exceptions.generation import GenerationException

        with pytest.raises(GenerationException, match="already exists"):
            generate_use_case.execute(spec, tmp_path)

    def test_generation_result_metadata(self, generate_use_case, tmp_path):
        """Test that generation result contains useful metadata."""
        spec = ProjectSpec(
            project_name=ProjectName("test-service"),
            template_version=TemplateVersion("1.0.0"),
            modules=frozenset(),
        )

        result = generate_use_case.execute(spec, tmp_path)

        # Verify result metadata
        assert result.correlation_id == spec.correlation_id
        assert result.duration_seconds > 0
        assert result.completed_at is not None
        assert len(result.files_created) > 0
        assert result.total_files > 0

    def test_generated_project_is_valid_python(self, generate_use_case, tmp_path):
        """Test that generated Python files are syntactically valid."""
        spec = ProjectSpec(
            project_name=ProjectName("test-service"),
            template_version=TemplateVersion("1.0.0"),
            modules=frozenset(),
        )

        generate_use_case.execute(spec, tmp_path)
        project_path = tmp_path / "test-service"

        # Try to compile all Python files
        import py_compile

        python_files = list(project_path.rglob("*.py"))
        assert len(python_files) > 0

        for py_file in python_files:
            # This will raise SyntaxError if file is invalid
            py_compile.compile(str(py_file), doraise=True)
