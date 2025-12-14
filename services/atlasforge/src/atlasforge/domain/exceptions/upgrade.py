"""Upgrade exceptions."""

from atlasforge.domain.exceptions.base import AtlasForgeException


class UpgradeException(AtlasForgeException):
    """Raised when project upgrade fails."""

    pass
