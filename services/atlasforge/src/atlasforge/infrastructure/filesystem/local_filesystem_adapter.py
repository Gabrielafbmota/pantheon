"""Local filesystem adapter implementation."""

from pathlib import Path
from typing import List
import shutil

from atlasforge.domain.ports.filesystem_port import IFileSystemPort


class LocalFileSystemAdapter(IFileSystemPort):
    """
    Implements filesystem operations using standard library.

    This adapter uses pathlib.Path for all operations, providing
    cross-platform compatibility.
    """

    def exists(self, path: Path) -> bool:
        """Check if a path exists."""
        return path.exists()

    def is_file(self, path: Path) -> bool:
        """Check if path is a file."""
        return path.is_file()

    def is_dir(self, path: Path) -> bool:
        """Check if path is a directory."""
        return path.is_dir()

    def read_file(self, path: Path) -> str:
        """Read file content as string."""
        return path.read_text(encoding="utf-8")

    def read_bytes(self, path: Path) -> bytes:
        """Read file content as bytes."""
        return path.read_bytes()

    def write_file(self, path: Path, content: str) -> None:
        """Write string content to file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_bytes(self, path: Path, content: bytes) -> None:
        """Write bytes content to file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    def delete_file(self, path: Path) -> None:
        """Delete a file."""
        if path.exists() and path.is_file():
            path.unlink()

    def delete_dir(self, path: Path, recursive: bool = False) -> None:
        """Delete a directory."""
        if not path.exists():
            return

        if recursive:
            shutil.rmtree(path)
        else:
            path.rmdir()

    def create_dir(self, path: Path, parents: bool = True, exist_ok: bool = True) -> None:
        """Create a directory."""
        path.mkdir(parents=parents, exist_ok=exist_ok)

    def list_files(self, path: Path, recursive: bool = False, pattern: str = "*") -> List[Path]:
        """
        List files in a directory.

        Args:
            path: Directory to list
            recursive: If True, list recursively
            pattern: Glob pattern to filter files (e.g., "*.py")

        Returns:
            List of file paths (only files, not directories)
        """
        if not path.exists() or not path.is_dir():
            return []

        if recursive:
            # Use rglob for recursive search
            return [p for p in path.rglob(pattern) if p.is_file()]
        else:
            # Use glob for non-recursive search
            return [p for p in path.glob(pattern) if p.is_file()]

    def copy_file(self, source: Path, dest: Path) -> None:
        """Copy a file from source to destination."""
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)

    def move_file(self, source: Path, dest: Path) -> None:
        """Move a file from source to destination."""
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(dest))

    def get_file_size(self, path: Path) -> int:
        """Get file size in bytes."""
        return path.stat().st_size

    def get_modified_time(self, path: Path) -> float:
        """Get file modification time as timestamp."""
        return path.stat().st_mtime
