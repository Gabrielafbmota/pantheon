from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class SourceType(str, Enum):
    AEGIS = "aegis"
    EYE_OF_HORUS_OPS = "eye_of_horus_ops"
    ATLAS_FORGE = "atlas_forge"
    OTHER = "other"


@dataclass
class Source:
    id: str
    name: str
    type: SourceType


@dataclass
class Tag:
    key: str
    value: Optional[str] = None


@dataclass
class Version:
    fingerprint: str
    normalized_content: str
    summary: str
    tags: List[Tag]
    taxonomy: List[str]
    raw_uri: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class KnowledgeEntry:
    id: str
    source: Source
    external_id: str
    versions: List[Version] = field(default_factory=list)

    @property
    def latest_version(self) -> Optional[Version]:
        return self.versions[-1] if self.versions else None

    def add_version(self, version: Version) -> None:
        self.versions.append(version)


@dataclass
class AuditEvent:
    run_id: str
    step: str
    status: str
    entry_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    detail: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IngestionRun:
    run_id: str
    requests: List[Any]
    results: List[Any]
    status: str
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: Optional[datetime] = None
    audit_events: List[AuditEvent] = field(default_factory=list)
