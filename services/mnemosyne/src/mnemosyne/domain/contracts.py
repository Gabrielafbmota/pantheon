from __future__ import annotations

from typing import Iterable, List, Optional, Protocol

from mnemosyne.domain.entities.models import AuditEvent, IngestionRun, KnowledgeEntry


class KnowledgeRepository(Protocol):
    def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        ...

    def save_entry(self, entry: KnowledgeEntry) -> None:
        ...

    def list_entries(self) -> Iterable[KnowledgeEntry]:
        ...

    def record_run(self, run: IngestionRun) -> None:
        ...

    def get_run(self, run_id: str) -> Optional[IngestionRun]:
        ...

    def record_audit_events(self, events: List[AuditEvent]) -> None:
        ...


class TextIndex(Protocol):
    def index(self, entry: KnowledgeEntry) -> None:
        ...

    def search(
        self,
        text: Optional[str] = None,
        tags: Optional[List[str]] = None,
        taxonomy: Optional[List[str]] = None,
        source_types: Optional[List[str]] = None,
    ) -> List[str]:
        ...


class RawDocumentStorage(Protocol):
    """Abstraction for storing raw documents (e.g., S3, local)."""

    def store(self, run_id: str, external_id: str, content: str) -> str:
        """Persist raw content and return a URI/reference."""
        ...
