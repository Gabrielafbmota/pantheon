from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class Environment(str, Enum):
    PROD = "prod"
    STAGING = "staging"
    DEV = "dev"
    OTHER = "other"


@dataclass
class Service:
    id: str
    name: str
    env: Environment
    owners: List[str]
    logging_endpoint: Optional[str] = None
    health_url: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    otel_config: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, str] = field(default_factory=dict)


class SignalType(str, Enum):
    LOG = "log"
    METRIC = "metric"
    HEALTH = "health"
    ALERT = "alert"


@dataclass
class Signal:
    service_id: str
    type: SignalType
    message: str
    severity: str
    trace_id: Optional[str] = None
    correlation_id: Optional[str] = None
    timestamp: datetime = field(default_factory=now_utc)
    attributes: Dict[str, str] = field(default_factory=dict)


class IncidentStatus(str, Enum):
    OPEN = "open"
    MITIGATING = "mitigating"
    MONITORING = "monitoring"
    RESOLVED = "resolved"


@dataclass
class TimelineEvent:
    message: str
    actor: str
    event_type: str
    timestamp: datetime = field(default_factory=now_utc)
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None


@dataclass
class Incident:
    id: str
    service_id: str
    severity: str
    status: IncidentStatus
    summary: str
    signals: List[Signal] = field(default_factory=list)
    timeline: List[TimelineEvent] = field(default_factory=list)
    runbook_refs: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=now_utc)
    updated_at: datetime = field(default_factory=now_utc)
    correlation_id: Optional[str] = None

    def add_event(self, event: TimelineEvent) -> None:
        self.timeline.append(event)
        self.updated_at = event.timestamp

    def add_signal(self, signal: Signal) -> None:
        self.signals.append(signal)
        self.updated_at = now_utc()


@dataclass
class RunbookAction:
    id: str
    name: str
    description: str
    allowed_params: List[str]
    cooldown_seconds: int
    requires_approval: bool = False
    guardrails: Dict[str, str] = field(default_factory=dict)


class RemediationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class RemediationJob:
    id: str
    incident_id: str
    action_id: str
    service_id: str
    params: Dict[str, str]
    actor: str
    correlation_id: Optional[str]
    status: RemediationStatus = RemediationStatus.PENDING
    started_at: datetime = field(default_factory=now_utc)
    finished_at: Optional[datetime] = None
    output: Optional[str] = None
    error: Optional[str] = None

    def mark_started(self) -> None:
        self.status = RemediationStatus.RUNNING
        self.started_at = now_utc()

    def mark_completed(self, output: Optional[str] = None) -> None:
        self.status = RemediationStatus.COMPLETED
        self.finished_at = now_utc()
        self.output = output

    def mark_failed(self, error: str) -> None:
        self.status = RemediationStatus.FAILED
        self.finished_at = now_utc()
        self.error = error


def new_id() -> str:
    return str(uuid.uuid4())
