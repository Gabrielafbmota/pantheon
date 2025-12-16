from __future__ import annotations

import hashlib
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from mnemosyne.domain.entities.models import (
    AuditTrail,
    KnowledgeEntry,
    NormalizedDocument,
    Source,
    Tag,
    Version,
)
from mnemosyne.infrastructure.indexing.simple_index import SimpleTextIndex
from mnemosyne.infrastructure.persistence.repository import KnowledgeRepository


class IngestionRequest(NormalizedDocument):
    run_id: Optional[str] = None


class IngestionResult(NormalizedDocument):
    run_id: str
    deduplicated: bool
    entry_id: str
    version_id: str


class IngestionPipeline:
    def __init__(self, repository: KnowledgeRepository, index: SimpleTextIndex) -> None:
        self.repository = repository
        self.index = index

    def run(self, documents: List[IngestionRequest]) -> List[IngestionResult]:
        if not documents:
            return []
        run_id = documents[0].run_id or str(uuid4())
        if self.repository.has_run(run_id):
            existing_run = self.repository.get_run(run_id)
            return existing_run.get("results", []) if existing_run else []

        audit_trail = AuditTrail(run_id=run_id)
        normalized_docs = [self._normalize(doc) for doc in documents]
        self.repository.store_inputs(run_id, normalized_docs)

        results: List[IngestionResult] = []
        for doc in normalized_docs:
            audit_trail.record(step="fetch", status="ok", detail=doc.external_id)
            normalized_content = doc.content.strip()
            audit_trail.record(step="normalize", status="ok", detail=str(len(normalized_content)))
            fingerprint = self._fingerprint(normalized_content)
            enriched_tags = self._enrich(doc)
            audit_trail.record(step="enrich", status="ok", detail=fingerprint)
            summary = doc.manual_summary or self._summarize(normalized_content)
            audit_trail.record(step="summarize", status="ok", detail=str(len(summary)))

            existing = self.repository.find_by_fingerprint(fingerprint)
            if existing:
                entry_id, version = existing
                audit_trail.record(step="persist", status="deduplicated", detail=entry_id)
                result = IngestionResult(
                    external_id=doc.external_id,
                    source=doc.source,
                    content=normalized_content,
                    tags=doc.tags,
                    taxonomy=doc.taxonomy,
                    manual_summary=doc.manual_summary,
                    run_id=run_id,
                    deduplicated=True,
                    entry_id=entry_id,
                    version_id=version.version_id,
                )
                results.append(result)
                continue

            entry = self.repository.find_entry_by_source(doc.source.id, doc.external_id)
            version = Version(
                content=normalized_content,
                summary=summary,
                fingerprint=fingerprint,
                enriched_tags=enriched_tags,
                taxonomy=doc.taxonomy,
                run_id=run_id,
            )
            if entry:
                self.repository.add_version(entry.entry_id, version)
                audit_trail.record(step="persist", status="versioned", detail=entry.entry_id)
            else:
                entry = KnowledgeEntry(
                    source=doc.source,
                    external_id=doc.external_id,
                    tags=doc.tags,
                    taxonomy=doc.taxonomy,
                    versions=[version],
                )
                self.repository.save_entry(entry)
                audit_trail.record(step="persist", status="created", detail=entry.entry_id)

            self.index.index(entry.entry_id, f"{normalized_content} {summary}")
            audit_trail.record(step="index", status="ok", detail=entry.entry_id)

            results.append(
                IngestionResult(
                    external_id=doc.external_id,
                    source=doc.source,
                    content=normalized_content,
                    tags=doc.tags,
                    taxonomy=doc.taxonomy,
                    manual_summary=doc.manual_summary,
                    run_id=run_id,
                    deduplicated=False,
                    entry_id=entry.entry_id,
                    version_id=version.version_id,
                )
            )

        audit_trail.record(step="finish", status="ok", detail=str(len(results)))
        self.repository.attach_audit(run_id, audit_trail)
        entry_map = {entry.entry_id: entry for entry in self.repository.list_entries()}
        self.repository.update_run_entries(run_id, [entry_map[r.entry_id] for r in results])
        self.repository.store_run(
            run_id,
            {
                "results": results,
                "audit": audit_trail,
                "inputs": normalized_docs,
            },
        )
        return results

    def _fingerprint(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _normalize(self, doc: IngestionRequest) -> NormalizedDocument:
        normalized_content = "\n".join(line.strip() for line in doc.content.splitlines()).strip()
        taxonomy = list(dict.fromkeys(doc.taxonomy))
        return NormalizedDocument(
            external_id=doc.external_id,
            source=doc.source,
            content=normalized_content,
            tags=doc.tags,
            taxonomy=taxonomy,
            manual_summary=doc.manual_summary,
        )

    def _enrich(self, doc: NormalizedDocument) -> List[Tag]:
        inherited_tags = list(doc.tags)
        if doc.source.type:
            inherited_tags.append(Tag(key=f"source:{doc.source.type.value}"))
        return inherited_tags

    def _summarize(self, content: str) -> str:
        return content[:200] + ("…" if len(content) > 200 else "")
