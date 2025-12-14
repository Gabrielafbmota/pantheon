"""Checksum Port - Interface for checksum calculation."""

from abc import ABC, abstractmethod

from atlasforge.domain.value_objects.checksum import Checksum


class IChecksumPort(ABC):
    """
    Interface for checksum calculation operations.

    This port defines how checksums are calculated and verified.
    Implementations can use SHA256, MD5, or any other hashing algorithm.
    """

    @abstractmethod
    def calculate(self, content: str) -> Checksum:
        """
        Calculate checksum of string content.

        Args:
            content: String content to hash

        Returns:
            Checksum value object
        """
        pass

    @abstractmethod
    def calculate_bytes(self, content: bytes) -> Checksum:
        """
        Calculate checksum of bytes content.

        Args:
            content: Bytes content to hash

        Returns:
            Checksum value object
        """
        pass

    @abstractmethod
    def verify(self, content: str, expected: Checksum) -> bool:
        """
        Verify that content matches expected checksum.

        Args:
            content: String content to verify
            expected: Expected checksum

        Returns:
            True if content matches expected checksum
        """
        pass

    @abstractmethod
    def verify_bytes(self, content: bytes, expected: Checksum) -> bool:
        """
        Verify that bytes content matches expected checksum.

        Args:
            content: Bytes content to verify
            expected: Expected checksum

        Returns:
            True if content matches expected checksum
        """
        pass
