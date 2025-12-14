"""Template Engine Port - Interface for template rendering."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List


class ITemplateEnginePort(ABC):
    """
    Interface for template rendering operations.

    This port defines how templates are rendered.
    Implementations can use Jinja2, Mako, or any other template engine.
    """

    @abstractmethod
    def render_template(
        self, template_name: str, context: Dict[str, Any], output_path: Path
    ) -> List[str]:
        """
        Render a template directory to output path.

        Args:
            template_name: Name of the template (e.g., 'base', 'modules/mongo')
            context: Template context variables
            output_path: Where to write rendered files

        Returns:
            List of created file paths (relative to output_path)
        """
        pass

    @abstractmethod
    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """
        Render a template string with context.

        Args:
            template_string: Template content as string
            context: Template context variables

        Returns:
            Rendered string
        """
        pass

    @abstractmethod
    def render_file_to_string(self, template_path: Path, context: Dict[str, Any]) -> str:
        """
        Render a single template file to string.

        Args:
            template_path: Path to template file
            context: Template context variables

        Returns:
            Rendered content as string
        """
        pass

    @abstractmethod
    def get_available_templates(self) -> List[str]:
        """
        Get list of available template names.

        Returns:
            List of template names (e.g., ['base', 'modules/mongo', 'modules/otel'])
        """
        pass
