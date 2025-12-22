from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from mnemosyne.domain.contracts import KnowledgeRepository
from mnemosyne.domain.entities.models import AuditEvent, IngestionRun, KnowledgeEntry


class InMemoryKnowledgeRepository(KnowledgeRepository):
    def __init__(self) -> None:
        self._entries: Dict[str, KnowledgeEntry] = {}
        self._runs: Dict[str, IngestionRun] = {}
        self._audit_events: List[AuditEvent] = []

    def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        return self._entries.get(entry_id)

    def save_entry(self, entry: KnowledgeEntry) -> None:
        self._entries[entry.id] = entry

    def list_entries(self) -> Iterable[KnowledgeEntry]:
        return list(self._entries.values())

    def record_run(self, run: IngestionRun) -> None:
        self._runs[run.run_id] = run

    def get_run(self, run_id: str) -> Optional[IngestionRun]:
        return self._runs.get(run_id)

    def record_audit_events(self, events: List[AuditEvent]) -> None:
        self._audit_events.extend(events)

    @property
    def audit_log(self) -> List[AuditEvent]:
        return list(self._audit_events)
