from __future__ import annotations

import os
from datetime import datetime
from typing import Dict, Iterable, List, Optional

from pymongo import MongoClient
from pymongo.collection import Collection

from mnemosyne.domain.contracts import KnowledgeRepository
from mnemosyne.domain.entities.models import AuditEvent, IngestionRun, KnowledgeEntry, Source, SourceType, Tag, Version


def _client_from_env() -> MongoClient:
    uri = os.getenv("MNEMO_MONGO_URI", "mongodb://localhost:27017")
    return MongoClient(uri, serverSelectionTimeoutMS=2000, connectTimeoutMS=2000)


def _db_name() -> str:
    return os.getenv("MNEMO_MONGO_DB", "mnemosyne")


def _as_dt(value: datetime | None) -> datetime | None:
    return value if value is None else value


def _parse_dt(value) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)


class MongoKnowledgeRepository(KnowledgeRepository):
    """Mongo-backed repository for knowledge entries and runs."""

    def __init__(self, client: MongoClient | None = None) -> None:
        client = client or _client_from_env()
        db = client[_db_name()]
        self._entries: Collection = db["entries"]
        self._runs: Collection = db["runs"]
        self._audit: Collection = db["audit"]
        self._entries.create_index("id", unique=True)
        self._runs.create_index("run_id", unique=True)
        self._audit.create_index("run_id")

    def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        doc = self._entries.find_one({"id": entry_id})
        if not doc:
            return None
        return self._entry_from_doc(doc)

    def save_entry(self, entry: KnowledgeEntry) -> None:
        doc = self._entry_to_doc(entry)
        self._entries.update_one({"id": entry.id}, {"$set": doc}, upsert=True)

    def list_entries(self) -> Iterable[KnowledgeEntry]:
        return [self._entry_from_doc(doc) for doc in self._entries.find({})]

    def record_run(self, run: IngestionRun) -> None:
        self._runs.update_one({"run_id": run.run_id}, {"$set": self._run_to_doc(run)}, upsert=True)

    def get_run(self, run_id: str) -> Optional[IngestionRun]:
        doc = self._runs.find_one({"run_id": run_id})
        if not doc:
            return None
        return self._run_from_doc(doc)

    def record_audit_events(self, events: List[AuditEvent]) -> None:
        if not events:
            return
        self._audit.insert_many([self._audit_to_doc(evt) for evt in events])

    # --- Serialization helpers ---
    def _entry_to_doc(self, entry: KnowledgeEntry) -> Dict:
        return {
            "id": entry.id,
            "source": {
                "id": entry.source.id,
                "name": entry.source.name,
                "type": entry.source.type.value if hasattr(entry.source.type, "value") else entry.source.type,
            },
            "external_id": entry.external_id,
            "versions": [
                {
                    "id": v.id,
                    "fingerprint": v.fingerprint,
                    "normalized_content": v.normalized_content,
                    "summary": v.summary,
                    "tags": [{"key": t.key, "value": t.value} for t in v.tags],
                    "taxonomy": v.taxonomy,
                    "raw_uri": v.raw_uri,
                    "created_at": _as_dt(v.created_at),
                }
                for v in entry.versions
            ],
        }

    def _entry_from_doc(self, doc: Dict) -> KnowledgeEntry:
        source_doc = doc["source"]
        entry = KnowledgeEntry(
            id=doc["id"],
            source=Source(
                id=source_doc["id"],
                name=source_doc["name"],
                type=SourceType(source_doc.get("type", SourceType.OTHER)),
            ),
            external_id=doc.get("external_id", ""),
        )
        for v in doc.get("versions", []):
            entry.add_version(
                Version(
                    id=v.get("id") or "",
                    fingerprint=v["fingerprint"],
                    normalized_content=v.get("normalized_content", ""),
                    summary=v.get("summary", ""),
                    tags=[Tag(key=t.get("key"), value=t.get("value")) for t in v.get("tags", [])],
                    taxonomy=v.get("taxonomy", []),
                    raw_uri=v.get("raw_uri"),
                    created_at=_parse_dt(v.get("created_at")) or datetime.utcnow(),
                )
            )
        return entry

    def _run_to_doc(self, run: IngestionRun) -> Dict:
        return {
            "run_id": run.run_id,
            "requests": [self._request_to_doc(r) for r in run.requests],
            "results": [self._result_to_doc(r) for r in run.results],
            "status": run.status,
            "started_at": _as_dt(run.started_at),
            "finished_at": _as_dt(run.finished_at),
            "audit_events": [self._audit_to_doc(evt) for evt in run.audit_events],
        }

    def _run_from_doc(self, doc: Dict) -> IngestionRun:
        return IngestionRun(
            run_id=doc["run_id"],
            requests=[self._request_from_doc(r) for r in doc.get("requests", [])],
            results=[self._result_from_doc(r) for r in doc.get("results", [])],
            status=doc.get("status", "completed"),
            started_at=_parse_dt(doc.get("started_at")) or datetime.utcnow(),
            finished_at=_parse_dt(doc.get("finished_at")),
            audit_events=[self._audit_from_doc(evt) for evt in doc.get("audit_events", [])],
        )

    def _audit_to_doc(self, evt: AuditEvent) -> Dict:
        return {
            "run_id": evt.run_id,
            "step": evt.step,
            "status": evt.status,
            "entry_id": evt.entry_id,
            "timestamp": _as_dt(evt.timestamp),
            "detail": evt.detail,
            "metadata": evt.metadata,
        }

    def _audit_from_doc(self, doc: Dict) -> AuditEvent:
        return AuditEvent(
            run_id=doc["run_id"],
            step=doc["step"],
            status=doc["status"],
            entry_id=doc["entry_id"],
            timestamp=_parse_dt(doc.get("timestamp")) or datetime.utcnow(),
            detail=doc.get("detail"),
            metadata=doc.get("metadata") or {},
        )

    def _request_to_doc(self, req) -> Dict:
        return req.__dict__

    def _request_from_doc(self, doc: Dict):
        from mnemosyne.application.use_cases.ingest import IngestionRequest

        source_raw = doc.get("source", {})
        if isinstance(source_raw, Source):
            source_doc = {"id": source_raw.id, "name": source_raw.name, "type": source_raw.type}
        else:
            source_doc = source_raw or {}
        return IngestionRequest(
            external_id=doc.get("external_id", ""),
            source=Source(
                id=source_doc.get("id", ""),
                name=source_doc.get("name", ""),
                type=source_doc.get("type", SourceType.OTHER),
            ),
            content=doc.get("content", ""),
            tags=[
                Tag(key=t.key, value=t.value) if isinstance(t, Tag) else Tag(key=t.get("key"), value=t.get("value"))
                for t in doc.get("tags", [])
            ],
            taxonomy=doc.get("taxonomy", []),
            summary=doc.get("summary"),
            run_id=doc.get("run_id"),
        )

    def _result_to_doc(self, result) -> Dict:
        return result.__dict__

    def _result_from_doc(self, doc: Dict):
        from mnemosyne.application.use_cases.ingest import IngestionResult

        return IngestionResult(
            entry_id=doc.get("entry_id", ""),
            version_id=doc.get("version_id", ""),
            fingerprint=doc.get("fingerprint", ""),
            run_id=doc.get("run_id", ""),
            deduplicated=doc.get("deduplicated", False),
        )
