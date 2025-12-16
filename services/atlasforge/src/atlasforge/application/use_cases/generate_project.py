"""GenerateProject Use Case - Orchestrates project generation."""

import logging
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from atlasforge.domain.entities.generation_result import GenerationResult
from atlasforge.domain.entities.project_spec import ProjectSpec
from atlasforge.domain.entities.template_manifest import ManagedFile, TemplateManifest
from atlasforge.domain.exceptions.generation import GenerationException
from atlasforge.domain.ports.checksum_port import IChecksumPort
from atlasforge.domain.ports.filesystem_port import IFileSystemPort
from atlasforge.domain.ports.manifest_repository_port import IManifestRepositoryPort
from atlasforge.domain.ports.module_port import IModulePort
from atlasforge.domain.ports.template_engine_port import ITemplateEnginePort
from atlasforge.domain.services.module_resolver import ModuleResolver
from atlasforge.domain.value_objects.file_path import FilePath

logger = logging.getLogger(__name__)


@dataclass
class GenerateProjectUseCase:
    """
    Generate a new project from template.

    Steps:
    1. Validate project doesn't exist
    2. Render base template
    3. Resolve and apply modules (if any)
    4. Calculate checksums for all files
    5. Create manifest
    6. Write manifest to project

    Supports modular project generation with mongo, otel, events, etc.
    """

    filesystem: IFileSystemPort
    template_engine: ITemplateEnginePort
    checksum: IChecksumPort
    manifest_repo: IManifestRepositoryPort
    module_loader: Optional[IModulePort] = None

    def execute(self, spec: ProjectSpec, target_dir: Path) -> GenerationResult:
        """
        Execute the generation.

        Args:
            spec: Project specification
            target_dir: Directory where project will be created

        Returns:
            GenerationResult with details of what was created

        Raises:
            GenerationException: If generation fails
        """
        start_time = time.time()
        project_path = target_dir / str(spec.project_name)

        result = GenerationResult(
            success=True,
            project_path=project_path,
            manifest=self._create_initial_manifest(spec),
            correlation_id=spec.correlation_id,
        )

        try:
            # 1. Validate project doesn't exist
            self._validate_project_can_be_created(project_path)

            # 2. Render base template
            base_files = self._render_base_template(spec, project_path)
            result.files_created.extend(base_files)

            # 3. Apply modules (if any)
            if spec.modules and self.module_loader:
                module_files = self._apply_modules(spec, project_path)
                result.files_created.extend(module_files)
                logger.info(
                    f"Applied {len(spec.modules)} modules",
                    extra={"modules": [str(m) for m in spec.modules]},
                )

            # 4. Calculate checksums
            self._update_manifest_checksums(result.manifest, project_path)

            # 5. Write manifest
            self.manifest_repo.save(result.manifest, project_path)
            result.files_created.append(".atlasforge/manifest.json")

        except Exception as e:
            result.add_error(str(e))
            raise GenerationException(f"Generation failed: {e}") from e
        finally:
            result.duration_seconds = time.time() - start_time
            result.completed_at = datetime.utcnow()

        return result

    def _validate_project_can_be_created(self, project_path: Path) -> None:
        """
        Check if project can be created.

        Raises:
            GenerationException: If project already exists
        """
        if self.filesystem.exists(project_path):
            raise GenerationException(f"Project directory already exists: {project_path}")

    def _create_initial_manifest(self, spec: ProjectSpec) -> TemplateManifest:
        """Create initial manifest from spec."""
        return TemplateManifest(
            template_name="atlas-base",
            template_version=spec.template_version,
            project_name=str(spec.project_name),
            modules_enabled=list(spec.modules),
            managed_files={},
            generated_at=datetime.utcnow(),
            correlation_id=spec.correlation_id,
        )

    def _render_base_template(self, spec: ProjectSpec, project_path: Path) -> list[str]:
        """
        Render base template files.

        Args:
            spec: Project specification
            project_path: Where to create project

        Returns:
            List of created file paths (relative to project_path)
        """
        context = {
            "project_name": str(spec.project_name),
            "template_version": str(spec.template_version),
            "correlation_id": spec.correlation_id,
            "modules": spec.module_list(),
        }

        rendered_files = self.template_engine.render_template(
            template_name="base", context=context, output_path=project_path
        )

        return rendered_files

    def _apply_modules(self, spec: ProjectSpec, project_path: Path) -> list[str]:
        """
        Apply module files to the project.

        Args:
            spec: Project specification with modules
            project_path: Project root path

        Returns:
            List of created file paths (relative to project_path)
        """
        if not self.module_loader:
            logger.warning("Module loader not configured, skipping modules")
            return []

        created_files = []

        try:
            # Load all modules
            modules = self.module_loader.load_modules(spec.modules)

            # Resolve module order (topological sort for dependencies)
            resolver = ModuleResolver()
            ordered_modules = resolver.resolve_order(modules)

            logger.info(
                f"Resolved {len(ordered_modules)} modules",
                extra={"order": [str(m.name) for m in ordered_modules]},
            )

            # Apply each module
            for module in ordered_modules:
                logger.info(f"Applying module: {module.name}")

                # Render module files
                context = {
                    "project_name": str(spec.project_name),
                    "template_version": str(spec.template_version),
                    "modules": spec.module_list(),
                }

                # Render each file in the module
                for module_file in module.files:
                    try:
                        # Render the module file
                        created_path = self.template_engine.render_module_file(
                            module_name=module.name.value,
                            source_file=module_file.source,
                            destination=module_file.destination,
                            context=context,
                            output_path=project_path,
                        )
                        created_files.append(created_path)
                        logger.debug(f"Rendered module file: {created_path}")
                    except Exception as e:
                        logger.error(
                            f"Failed to render module file {module_file.source}: {e}"
                        )
                        raise

        except Exception as e:
            logger.error(f"Failed to apply modules: {e}")
            raise GenerationException(f"Module application failed: {e}") from e

        return created_files

    def _update_manifest_checksums(
        self, manifest: TemplateManifest, project_path: Path
    ) -> None:
        """
        Calculate and store checksums for all managed files.

        Args:
            manifest: Manifest to update
            project_path: Root of the project
        """
        # Get all files except .atlasforge directory
        all_files = self.filesystem.list_files(project_path, recursive=True)

        for file_path in all_files:
            # Skip .atlasforge directory
            if ".atlasforge" in str(file_path):
                continue

            # Read content and calculate checksum
            content = self.filesystem.read_file(file_path)
            file_checksum = self.checksum.calculate(content)

            # Get relative path
            relative_path = file_path.relative_to(project_path)
            fp = FilePath.from_path(Path(relative_path))

            # Determine if file is user-editable
            is_editable = self._is_user_editable(fp)

            # Add to manifest
            managed_file = ManagedFile(
                path=fp, checksum=file_checksum, source="base", is_user_editable=is_editable
            )
            manifest.add_managed_file(managed_file)

    def _is_user_editable(self, path: FilePath) -> bool:
        """
        Determine if file is expected to be edited by users.

        Files in domain/application are user-editable.
        Files in infrastructure/presentation might be.
        Configuration files are not.

        Args:
            path: File path to check

        Returns:
            True if file is expected to be edited by users
        """
        path_str = str(path.value)

        # User-editable patterns
        editable_patterns = [
            "/domain/",
            "/application/",
            "tests/",
            "README.md",
        ]

        # Not editable patterns (take precedence)
        not_editable_patterns = [
            "pyproject.toml",
            "Dockerfile",
            ".gitignore",
            "/presentation/api/main.py",  # Generated API entry point
        ]

        # Check not-editable first
        for pattern in not_editable_patterns:
            if pattern in path_str:
                return False

        # Check editable
        for pattern in editable_patterns:
            if pattern in path_str:
                return True

        # Default: infrastructure files are semi-editable
        return "/infrastructure/" in path_str
