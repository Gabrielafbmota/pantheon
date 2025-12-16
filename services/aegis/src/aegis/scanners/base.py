from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from ..models import Finding


class Scanner(ABC):
    """Base class for all scanners/detectors."""

    @abstractmethod
    def scan(self, repo_path: str) -> List[Finding]:
        """Run the scanner and return findings."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Scanner name for logging and identification."""
        pass
