from __future__ import annotations

import hashlib
import textwrap
import uuid
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import List, Optional

from mnemosyne.domain.contracts import KnowledgeRepository, RawDocumentStorage, TextIndex
from mnemosyne.domain.entities.models import AuditEvent, KnowledgeEntry, Source, Tag, Version


@dataclass
class IngestionRequest:
    external_id: str
    source: Source
    content: str
    tags: List[Tag] = field(default_factory=list)
    taxonomy: List[str] = field(default_factory=list)
    summary: Optional[str] = None
    run_id: Optional[str] = None


@dataclass
class IngestionResult:
    entry_id: str
    version_id: str
    fingerprint: str
    run_id: str
    deduplicated: bool = False


class IngestionPipeline:
    def __init__(
        self,
        repository: KnowledgeRepository,
        index: TextIndex,
        storage: RawDocumentStorage | None = None,
    ) -> None:
        self.repository = repository
        self.index = index
        self.storage = storage

    def run(self, requests: List[IngestionRequest]) -> List[IngestionResult]:
        results: List[IngestionResult] = []

        for request in requests:
            run_id = request.run_id or str(uuid.uuid4())

            # Idempotent: return previous run if already processed
            existing_run = self.repository.get_run(run_id)
            if existing_run:
                results.extend(existing_run.results)
                continue

            audit_events: List[AuditEvent] = []

            # Persist raw content if storage configured
            raw_uri = None
            if self.storage:
                raw_uri = self.storage.store(run_id=run_id, external_id=request.external_id, content=request.content)
                audit_events.append(
                    AuditEvent(
                        run_id=run_id,
                        step="persist_raw",
                        status="ok",
                        entry_id=request.external_id,
                        metadata={"uri": raw_uri},
                    )
                )

            # Normalize
            normalized_content = self._normalize(request.content)
            audit_events.append(AuditEvent(run_id=run_id, step="normalize", status="ok", entry_id=request.external_id))

            # Enrich
            fingerprint = self._fingerprint(normalized_content)
            audit_events.append(AuditEvent(run_id=run_id, step="enrich", status="ok", entry_id=request.external_id))

            # Summarize
            summary = request.summary or self._summarize(normalized_content)
            audit_events.append(AuditEvent(run_id=run_id, step="summarize", status="ok", entry_id=request.external_id))

            # Persist + versioning
            entry_id = f"{request.source.id}:{request.external_id}"
            entry = self.repository.get_entry(entry_id)
            deduplicated = False

            if entry and entry.latest_version and entry.latest_version.fingerprint == fingerprint:
                deduplicated = True
                audit_events.append(AuditEvent(run_id=run_id, step="persist", status="deduplicated", entry_id=entry_id))
            else:
                if not entry:
                    entry = KnowledgeEntry(id=entry_id, source=request.source, external_id=request.external_id)
                version = Version(
                    fingerprint=fingerprint,
                    normalized_content=normalized_content,
                    summary=summary,
                    tags=request.tags,
                    taxonomy=request.taxonomy,
                    raw_uri=raw_uri,
                )
                entry.add_version(version)
                self.repository.save_entry(entry)
                audit_events.append(AuditEvent(run_id=run_id, step="persist", status="versioned", entry_id=entry_id))

            # Index latest version for search
            self.index.index(entry)
            audit_events.append(AuditEvent(run_id=run_id, step="index", status="ok", entry_id=entry_id))

            result = IngestionResult(
                entry_id=entry.id,
                version_id=entry.latest_version.id if entry.latest_version else "",
                fingerprint=fingerprint,
                run_id=run_id,
                deduplicated=deduplicated,
            )
            results.append(result)

            self.repository.record_run(
                self._build_run(run_id=run_id, request=request, result=result, audit_events=audit_events)
            )
            self.repository.record_audit_events(audit_events)

        return results

    def _build_run(
        self, run_id: str, request: IngestionRequest, result: IngestionResult, audit_events: List[AuditEvent]
    ):
        from mnemosyne.domain.entities.models import IngestionRun

        recorded_request = replace(request, run_id=run_id)

        return IngestionRun(
            run_id=run_id,
            requests=[recorded_request],
            results=[result],
            status="completed",
            audit_events=audit_events,
            finished_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def _normalize(content: str) -> str:
        return "\n".join(line.strip() for line in content.strip().splitlines())

    @staticmethod
    def _fingerprint(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def _summarize(content: str) -> str:
        single_line = " ".join(content.split())
        return textwrap.shorten(single_line, width=140, placeholder="...")
