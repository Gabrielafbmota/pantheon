from __future__ import annotations

from typing import Any, Dict
import logging

logger = logging.getLogger("aegis.adapters.events")


class MnemosynePublisher:
    """Stub publisher for Mnemosyne that would create a KnowledgeEntry."""

    def publish(self, scan: Dict[str, Any]) -> str:
        logger.info("publish knowledge entry", extra={"scan_repo": scan.get("repo")})
        # Return a fake id for MVP
        return "mnemosyne:fake-id"


class EyeOfHorusPublisher:
    """Stub publisher for EyeOfHorusOps that would emit a violation event."""

    def emit(self, event: Dict[str, Any]) -> str:
        logger.warning("emit event", extra={"event": event})
        return "eyeofhorus:fake-event"
