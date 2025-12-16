from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple

from mnemosyne.domain.entities.models import (
    AuditTrail,
    KnowledgeEntry,
    NormalizedDocument,
    Version,
)


class KnowledgeRepository:
    def has_run(self, run_id: str) -> bool:
        raise NotImplementedError

    def store_run(self, run_id: str, run: Dict) -> None:
        raise NotImplementedError

    def get_run(self, run_id: str) -> Optional[Dict]:
        raise NotImplementedError

    def find_by_fingerprint(self, fingerprint: str) -> Optional[Tuple[str, Version]]:
        raise NotImplementedError

    def save_entry(self, entry: KnowledgeEntry) -> None:
        raise NotImplementedError

    def add_version(self, entry_id: str, version: Version) -> KnowledgeEntry:
        raise NotImplementedError

    def list_entries(self) -> Iterable[KnowledgeEntry]:
        raise NotImplementedError

    def find_entry_by_source(self, source_id: str, external_id: str) -> Optional[KnowledgeEntry]:
        raise NotImplementedError

    def search(
        self,
        text: Optional[str] = None,
        tags: Optional[List[str]] = None,
        source_types: Optional[List[str]] = None,
        taxonomy: Optional[List[str]] = None,
    ) -> List[KnowledgeEntry]:
        raise NotImplementedError

    def attach_audit(self, run_id: str, audit_trail: AuditTrail) -> None:
        raise NotImplementedError

    def update_run_entries(self, run_id: str, entries: List[KnowledgeEntry]) -> None:
        raise NotImplementedError

    def store_inputs(self, run_id: str, inputs: List[NormalizedDocument]) -> None:
        raise NotImplementedError
