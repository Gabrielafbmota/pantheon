from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple

from mnemosyne.domain.entities.models import AuditTrail, KnowledgeEntry, NormalizedDocument, Version
from mnemosyne.infrastructure.persistence.repository import KnowledgeRepository


class InMemoryKnowledgeRepository(KnowledgeRepository):
    def __init__(self) -> None:
        self._entries: Dict[str, KnowledgeEntry] = {}
        self._fingerprints: Dict[str, Tuple[str, Version]] = {}
        self._runs: Dict[str, Dict] = {}

    def has_run(self, run_id: str) -> bool:
        return run_id in self._runs

    def store_run(self, run_id: str, run: Dict) -> None:
        self._runs[run_id] = run

    def get_run(self, run_id: str) -> Optional[Dict]:
        return self._runs.get(run_id)

    def find_by_fingerprint(self, fingerprint: str) -> Optional[Tuple[str, Version]]:
        return self._fingerprints.get(fingerprint)

    def save_entry(self, entry: KnowledgeEntry) -> None:
        self._entries[entry.entry_id] = entry
        if entry.latest_version:
            self._fingerprints[entry.latest_version.fingerprint] = (entry.entry_id, entry.latest_version)

    def add_version(self, entry_id: str, version: Version) -> KnowledgeEntry:
        entry = self._entries[entry_id]
        entry.versions.append(version)
        self._fingerprints[version.fingerprint] = (entry_id, version)
        return entry

    def list_entries(self) -> Iterable[KnowledgeEntry]:
        return list(self._entries.values())

    def find_entry_by_source(self, source_id: str, external_id: str) -> Optional[KnowledgeEntry]:
        for entry in self._entries.values():
            if entry.source.id == source_id and entry.external_id == external_id:
                return entry
        return None

    def search(
        self,
        text: Optional[str] = None,
        tags: Optional[List[str]] = None,
        source_types: Optional[List[str]] = None,
        taxonomy: Optional[List[str]] = None,
    ) -> List[KnowledgeEntry]:
        results: List[KnowledgeEntry] = []
        for entry in self._entries.values():
            if source_types and entry.source.type.value not in source_types:
                continue
            if tags:
                tag_keys = {tag.key for tag in entry.tags + entry.latest_version.enriched_tags if entry.latest_version}
                if not set(tags).issubset(tag_keys):
                    continue
            if taxonomy:
                if not set(taxonomy).issubset(set(entry.taxonomy)):
                    continue
            if text:
                latest = entry.latest_version
                if latest is None:
                    continue
                if text.lower() not in latest.content.lower() and text.lower() not in latest.summary.lower():
                    continue
            results.append(entry)
        return results

    def attach_audit(self, run_id: str, audit_trail: AuditTrail) -> None:
        run = self._runs.setdefault(run_id, {})
        run["audit"] = audit_trail

    def update_run_entries(self, run_id: str, entries: List[KnowledgeEntry]) -> None:
        run = self._runs.setdefault(run_id, {})
        run["entries"] = entries

    def store_inputs(self, run_id: str, inputs: List[NormalizedDocument]) -> None:
        run = self._runs.setdefault(run_id, {})
        run["inputs"] = inputs
