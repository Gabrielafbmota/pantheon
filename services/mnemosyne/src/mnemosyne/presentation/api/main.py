from __future__ import annotations

import os
from typing import List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from mnemosyne.application.use_cases.ingest import IngestionPipeline, IngestionRequest
from mnemosyne.application.use_cases.reprocess import ReprocessIngestionUseCase
from mnemosyne.application.use_cases.search import SearchKnowledgeUseCase
from mnemosyne.domain.entities.models import AuditEvent, KnowledgeEntry, Source, SourceType, Tag
from mnemosyne.infrastructure.indexing import MongoTextIndex, SimpleTextIndex
from mnemosyne.infrastructure.observability import Observability
from mnemosyne.infrastructure.persistence import InMemoryKnowledgeRepository, MongoKnowledgeRepository
from mnemosyne.infrastructure.storage import S3RawDocumentStorage

app = FastAPI(title="Mnemosyne", version="0.1.1")
observability = Observability(service_name="mnemosyne")
observability.instrument_fastapi(app)


def _build_repository():
    if PERSISTENCE_BACKEND == "mongo":
        return MongoKnowledgeRepository()
    return InMemoryKnowledgeRepository()


def _build_index(repo):
    if PERSISTENCE_BACKEND == "mongo" and isinstance(repo, MongoKnowledgeRepository):
        collection = repo._entries.database["index"]  # type: ignore[attr-defined] # pragma: no cover - runtime only
        return MongoTextIndex(collection)
    return SimpleTextIndex()


def _build_storage():
    if S3_BUCKET:
        return S3RawDocumentStorage(bucket=S3_BUCKET)
    return None


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    configured = os.getenv("MNEMO_API_KEY")
    if configured and x_api_key != configured:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid api key")


def _to_ingestion_requests(payloads: List["IngestionPayload"]) -> List[IngestionRequest]:
    requests: List[IngestionRequest] = []
    for payload in payloads:
        src = Source(id=payload.source.id, name=payload.source.name, type=payload.source.type)
        tags = [Tag(key=t.key, value=t.value) for t in payload.tags]
        requests.append(
            IngestionRequest(
                external_id=payload.external_id,
                source=src,
                content=payload.content,
                tags=tags,
                taxonomy=payload.taxonomy,
                summary=payload.summary,
                run_id=payload.run_id,
            )
        )
    return requests


class TagModel(BaseModel):
    key: str
    value: str | None = None


class SourceModel(BaseModel):
    id: str
    name: str
    type: SourceType = SourceType.OTHER


class IngestionPayload(BaseModel):
    external_id: str
    source: SourceModel
    content: str
    tags: List[TagModel] = Field(default_factory=list)
    taxonomy: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    run_id: Optional[str] = None


class VersionOut(BaseModel):
    id: str
    summary: str
    fingerprint: str
    tags: List[TagModel]
    taxonomy: List[str]
    raw_uri: str | None = None


class KnowledgeEntryOut(BaseModel):
    id: str
    source: SourceModel
    external_id: str
    versions: List[VersionOut]


class AuditEventOut(BaseModel):
    run_id: str
    step: str
    status: str
    entry_id: str
    detail: str | None = None
    metadata: dict = Field(default_factory=dict)


def _serialize_entry(entry: KnowledgeEntry) -> KnowledgeEntryOut:
    return KnowledgeEntryOut(
        id=entry.id,
        external_id=entry.external_id,
        source=SourceModel(id=entry.source.id, name=entry.source.name, type=entry.source.type),
        versions=[
            VersionOut(
                id=v.id,
                summary=v.summary,
                fingerprint=v.fingerprint,
                tags=[TagModel(key=t.key, value=t.value) for t in v.tags],
                taxonomy=v.taxonomy,
                raw_uri=v.raw_uri,
            )
            for v in entry.versions
        ],
    )


def _serialize_audit(events: List[AuditEvent]) -> List[AuditEventOut]:
    return [
        AuditEventOut(
            run_id=e.run_id,
            step=e.step,
            status=e.status,
            entry_id=e.entry_id,
            detail=e.detail,
            metadata=e.metadata,
        )
        for e in events
    ]


PERSISTENCE_BACKEND = os.getenv("MNEMO_PERSISTENCE", "memory").lower()
S3_BUCKET = os.getenv("MNEMO_S3_BUCKET")

repository = _build_repository()
index = _build_index(repository)
storage = _build_storage()
pipeline = IngestionPipeline(repository=repository, index=index, storage=storage)
search_use_case = SearchKnowledgeUseCase(repository=repository, index=index)
reprocess_use_case = ReprocessIngestionUseCase(repository=repository, pipeline=pipeline)


@app.get("/health")
def health():
    return {"status": "ok", "service": "mnemosyne"}


@app.post("/ingestions", dependencies=[Depends(require_api_key)])
def ingest(documents: List[IngestionPayload]):
    results = pipeline.run(_to_ingestion_requests(documents))
    if results:
        observability.ingestions_counter.add(len(results))
    return results


@app.get("/search", dependencies=[Depends(require_api_key)])
def search(
    text: str | None = None,
    tags: str | None = None,
    source_types: str | None = None,
    taxonomy: str | None = None,
):
    tag_list = tags.split(",") if tags else None
    source_type_list = source_types.split(",") if source_types else None
    taxonomy_list = taxonomy.split(",") if taxonomy else None
    results = search_use_case.execute(text=text, tags=tag_list, source_types=source_type_list, taxonomy=taxonomy_list)
    observability.search_counter.add(len(results))
    return [_serialize_entry(entry) for entry in results]


@app.post("/reprocess/{run_id}", dependencies=[Depends(require_api_key)])
def reprocess(run_id: str):
    try:
        results = reprocess_use_case.execute(run_id)
        observability.ingestions_counter.add(len(results))
        return results
    except ValueError as exc:  # pragma: no cover - FastAPI handles response
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/runs/{run_id}", dependencies=[Depends(require_api_key)])
def get_run(run_id: str):
    run = repository.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run not found")
    return {
        "run_id": run.run_id,
        "status": run.status,
        "requests": [r.__dict__ for r in run.requests],
        "results": [r.__dict__ for r in run.results],
        "audit_events": _serialize_audit(run.audit_events),
    }
