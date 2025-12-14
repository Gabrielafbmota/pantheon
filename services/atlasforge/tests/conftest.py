"""Pytest configuration and shared fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def tmp_project_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory for project generation tests."""
    project_dir = tmp_path / "test_projects"
    project_dir.mkdir()
    return project_dir
