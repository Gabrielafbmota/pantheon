"""FileSystem Port - Interface for filesystem operations."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List


class IFileSystemPort(ABC):
    """
    Interface for filesystem operations.

    This port defines all filesystem operations needed by the domain.
    Implementations can use local filesystem, S3, or any other storage.
    """

    @abstractmethod
    def exists(self, path: Path) -> bool:
        """Check if a path exists."""
        pass

    @abstractmethod
    def is_file(self, path: Path) -> bool:
        """Check if path is a file."""
        pass

    @abstractmethod
    def is_dir(self, path: Path) -> bool:
        """Check if path is a directory."""
        pass

    @abstractmethod
    def read_file(self, path: Path) -> str:
        """Read file content as string."""
        pass

    @abstractmethod
    def read_bytes(self, path: Path) -> bytes:
        """Read file content as bytes."""
        pass

    @abstractmethod
    def write_file(self, path: Path, content: str) -> None:
        """Write string content to file."""
        pass

    @abstractmethod
    def write_bytes(self, path: Path, content: bytes) -> None:
        """Write bytes content to file."""
        pass

    @abstractmethod
    def delete_file(self, path: Path) -> None:
        """Delete a file."""
        pass

    @abstractmethod
    def delete_dir(self, path: Path, recursive: bool = False) -> None:
        """Delete a directory."""
        pass

    @abstractmethod
    def create_dir(self, path: Path, parents: bool = True, exist_ok: bool = True) -> None:
        """Create a directory."""
        pass

    @abstractmethod
    def list_files(self, path: Path, recursive: bool = False, pattern: str = "*") -> List[Path]:
        """
        List files in a directory.

        Args:
            path: Directory to list
            recursive: If True, list recursively
            pattern: Glob pattern to filter files (e.g., "*.py")

        Returns:
            List of file paths
        """
        pass

    @abstractmethod
    def copy_file(self, source: Path, dest: Path) -> None:
        """Copy a file from source to destination."""
        pass

    @abstractmethod
    def move_file(self, source: Path, dest: Path) -> None:
        """Move a file from source to destination."""
        pass

    @abstractmethod
    def get_file_size(self, path: Path) -> int:
        """Get file size in bytes."""
        pass

    @abstractmethod
    def get_modified_time(self, path: Path) -> float:
        """Get file modification time as timestamp."""
        pass
