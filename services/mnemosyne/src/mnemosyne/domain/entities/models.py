from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class SourceType(str, Enum):
    AEGIS = "aegis"
    EYE_OF_HORUS_OPS = "eye_of_horus_ops"
    ATLAS_FORGE = "atlas_forge"
    OTHER = "other"


class Source(BaseModel):
    id: str
    name: str
    type: SourceType
    metadata: Dict[str, str] = Field(default_factory=dict)


class Tag(BaseModel):
    key: str
    value: Optional[str] = None


class Version(BaseModel):
    version_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    content: str
    summary: str
    fingerprint: str
    enriched_tags: List[Tag] = Field(default_factory=list)
    taxonomy: List[str] = Field(default_factory=list)
    run_id: str


class AuditEvent(BaseModel):
    step: str
    status: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AuditTrail(BaseModel):
    run_id: str
    events: List[AuditEvent] = Field(default_factory=list)

    def record(self, step: str, status: str, detail: Optional[str] = None) -> None:
        self.events.append(AuditEvent(step=step, status=status, detail=detail))


class KnowledgeEntry(BaseModel):
    entry_id: str = Field(default_factory=lambda: str(uuid4()))
    source: Source
    external_id: str
    tags: List[Tag] = Field(default_factory=list)
    taxonomy: List[str] = Field(default_factory=list)
    versions: List[Version] = Field(default_factory=list)

    @property
    def latest_version(self) -> Optional[Version]:
        if not self.versions:
            return None
        return sorted(self.versions, key=lambda v: v.created_at)[-1]


class NormalizedDocument(BaseModel):
    external_id: str
    source: Source
    content: str
    tags: List[Tag] = Field(default_factory=list)
    taxonomy: List[str] = Field(default_factory=list)
    manual_summary: Optional[str] = None


class IngestionRun(BaseModel):
    run_id: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    status: str = "pending"
    audit_trail: AuditTrail
    inputs: List[NormalizedDocument] = Field(default_factory=list)
    produced_entries: List[KnowledgeEntry] = Field(default_factory=list)

    def complete(self, status: str) -> None:
        self.status = status
        self.finished_at = datetime.utcnow()
