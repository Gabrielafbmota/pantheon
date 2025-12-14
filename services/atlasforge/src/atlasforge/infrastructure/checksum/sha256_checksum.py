"""SHA256 checksum implementation."""

import hashlib

from atlasforge.domain.ports.checksum_port import IChecksumPort
from atlasforge.domain.value_objects.checksum import Checksum


class SHA256ChecksumAdapter(IChecksumPort):
    """
    SHA256-based checksum calculation.

    Provides strong collision resistance suitable for
    detecting file modifications in upgrade scenarios.
    """

    def calculate(self, content: str) -> Checksum:
        """
        Calculate SHA256 checksum of string content.

        Args:
            content: String content to hash

        Returns:
            Checksum value object with 64-char hex digest
        """
        hash_obj = hashlib.sha256(content.encode("utf-8"))
        return Checksum(hash_obj.hexdigest())

    def calculate_bytes(self, content: bytes) -> Checksum:
        """
        Calculate SHA256 checksum of bytes content.

        Args:
            content: Bytes content to hash

        Returns:
            Checksum value object with 64-char hex digest
        """
        hash_obj = hashlib.sha256(content)
        return Checksum(hash_obj.hexdigest())

    def verify(self, content: str, expected: Checksum) -> bool:
        """
        Verify that content matches expected checksum.

        Args:
            content: String content to verify
            expected: Expected checksum

        Returns:
            True if content matches expected checksum
        """
        actual = self.calculate(content)
        return actual == expected

    def verify_bytes(self, content: bytes, expected: Checksum) -> bool:
        """
        Verify that bytes content matches expected checksum.

        Args:
            content: Bytes content to verify
            expected: Expected checksum

        Returns:
            True if content matches expected checksum
        """
        actual = self.calculate_bytes(content)
        return actual == expected
