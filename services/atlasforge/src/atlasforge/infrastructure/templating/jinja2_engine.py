"""Jinja2 template engine adapter."""

import sys
from pathlib import Path
from typing import Any, Dict, List

import jinja2

from atlasforge.domain.ports.template_engine_port import ITemplateEnginePort


class Jinja2TemplateEngine(ITemplateEnginePort):
    """
    Jinja2-based template rendering.

    Templates are loaded from the templates/ directory bundled with AtlasForge.
    Supports custom filters for code generation (snake_case, pascal_case).
    """

    def __init__(self, templates_dir: Path):
        """
        Initialize Jinja2 engine.

        Args:
            templates_dir: Root directory containing templates
        """
        self.templates_dir = templates_dir

        # Create Jinja2 environment
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(templates_dir)),
            autoescape=False,  # We're generating code, not HTML
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Register custom filters
        self.env.filters["snake_case"] = self._snake_case
        self.env.filters["pascal_case"] = self._pascal_case
        self.env.filters["kebab_case"] = self._kebab_case

    def render_template(
        self, template_name: str, context: Dict[str, Any], output_path: Path
    ) -> List[str]:
        """
        Render a template directory to output path.

        Processes all files in template_name/project/ directory.
        Files ending with .j2 are rendered as Jinja2 templates.
        Path names can contain template variables (e.g., {{project_name}}).

        Args:
            template_name: Name of the template (e.g., 'base', 'modules/mongo')
            context: Template context variables
            output_path: Where to write rendered files

        Returns:
            List of created file paths (relative to output_path)
        """
        template_path = self.templates_dir / template_name / "project"
        created_files = []

        if not template_path.exists():
            raise ValueError(f"Template directory not found: {template_path}")

        # Get all files in template directory (sorted for determinism)
        all_files = sorted(template_path.rglob("*"))

        for template_file in all_files:
            if template_file.is_dir():
                continue

            # Calculate relative path
            rel_path = template_file.relative_to(template_path)

            # Render path (may contain {{project_name}} etc)
            rendered_path_str = self._render_string(str(rel_path), context)
            output_file = output_path / rendered_path_str

            # Remove .j2 extension if present
            if output_file.suffix == ".j2":
                output_file = output_file.with_suffix("")

            # Read and render content
            if template_file.suffix == ".j2":
                # Render as Jinja2 template
                template_rel = str(template_file.relative_to(self.templates_dir))
                template = self.env.get_template(template_rel)
                rendered_content = template.render(**context)
            else:
                # Copy as-is (binary files, etc.)
                rendered_content = template_file.read_text(encoding="utf-8")

            # Ensure parent directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            output_file.write_text(rendered_content, encoding="utf-8")

            created_files.append(str(output_file.relative_to(output_path)))

        return created_files

    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """
        Render a template string with context.

        Args:
            template_string: Template content as string
            context: Template context variables

        Returns:
            Rendered string
        """
        return self._render_string(template_string, context)

    def render_file_to_string(self, template_path: Path, context: Dict[str, Any]) -> str:
        """
        Render a single template file to string.

        Args:
            template_path: Path to template file (relative to templates_dir)
            context: Template context variables

        Returns:
            Rendered content as string
        """
        template_rel = str(template_path.relative_to(self.templates_dir))
        template = self.env.get_template(template_rel)
        return template.render(**context)

    def render_module_file(
        self,
        module_name: str,
        source_file: str,
        destination: str,
        context: Dict[str, Any],
        output_path: Path,
    ) -> str:
        """
        Render a single module file.

        Args:
            module_name: Name of the module (e.g., 'mongo', 'otel')
            source_file: Source file path relative to module files/ directory
            destination: Destination path (may contain template variables)
            context: Template context variables
            output_path: Root output path for the project

        Returns:
            Created file path (relative to output_path)
        """
        # Module files are in templates/modules/<module_name>/files/<source_file>
        template_file_path = (
            self.templates_dir / "modules" / module_name / "files" / source_file
        )

        if not template_file_path.exists():
            raise ValueError(f"Module template file not found: {template_file_path}")

        # Render destination path (may contain {{project_name}} etc)
        rendered_dest = self._render_string(destination, context)
        output_file = output_path / rendered_dest

        # Read and render content
        if template_file_path.suffix == ".j2":
            # Render as Jinja2 template
            template_rel = str(template_file_path.relative_to(self.templates_dir))
            template = self.env.get_template(template_rel)
            rendered_content = template.render(**context)

            # Remove .j2 extension from output
            if output_file.suffix == ".j2":
                output_file = output_file.with_suffix("")
        else:
            # Copy as-is
            rendered_content = template_file_path.read_text(encoding="utf-8")

        # Ensure parent directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        output_file.write_text(rendered_content, encoding="utf-8")

        return str(output_file.relative_to(output_path))

    def get_available_templates(self) -> List[str]:
        """
        Get list of available template names.

        Looks for directories containing a 'project' subdirectory.

        Returns:
            List of template names (e.g., ['base', 'modules/mongo'])
        """
        templates = []

        for item in self.templates_dir.rglob("*/project"):
            # Get parent directory name (the template name)
            template_name = str(item.parent.relative_to(self.templates_dir))
            templates.append(template_name)

        return sorted(templates)

    def _render_string(self, template_str: str, context: Dict[str, Any]) -> str:
        """Render a string template."""
        template = self.env.from_string(template_str)
        return template.render(**context)

    @staticmethod
    def _snake_case(value: str) -> str:
        """Convert to snake_case."""
        import re

        # Replace hyphens with underscores
        value = value.replace("-", "_")
        # Insert underscore before uppercase letters
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", value)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    @staticmethod
    def _pascal_case(value: str) -> str:
        """Convert to PascalCase."""
        # Split on hyphens and underscores
        parts = value.replace("-", "_").split("_")
        return "".join(word.capitalize() for word in parts if word)

    @staticmethod
    def _kebab_case(value: str) -> str:
        """Convert to kebab-case."""
        import re

        # Replace underscores with hyphens
        value = value.replace("_", "-")
        # Insert hyphen before uppercase letters
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1-\2", value)
        return re.sub("([a-z0-9])([A-Z])", r"\1-\2", s1).lower()
