from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Protocol

from eyeofhorusops.domain.entities import (
    Incident,
    RemediationJob,
    RunbookAction,
    Service,
    Signal,
    TimelineEvent,
)


class ServiceRepository(Protocol):
    def upsert(self, service: Service) -> None: ...

    def get(self, service_id: str) -> Optional[Service]: ...

    def list(self) -> Iterable[Service]: ...


class LogSink(Protocol):
    def ingest(self, service_id: str, record: Dict[str, str]) -> None: ...

    def search(
        self,
        service_id: Optional[str] = None,
        env: Optional[str] = None,
        level: Optional[str] = None,
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, str]]: ...


class IncidentRepository(Protocol):
    def save(self, incident: Incident) -> None: ...

    def get(self, incident_id: str) -> Optional[Incident]: ...

    def list(self) -> Iterable[Incident]: ...


class RunbookRepository(Protocol):
    def add_action(self, action: RunbookAction) -> None: ...

    def get_action(self, action_id: str) -> Optional[RunbookAction]: ...

    def list_actions(self) -> Iterable[RunbookAction]: ...

    def save_job(self, job: RemediationJob) -> None: ...

    def get_job(self, job_id: str) -> Optional[RemediationJob]: ...

    def list_jobs(self) -> Iterable[RemediationJob]: ...


class AuditLog(Protocol):
    def record(self, event: TimelineEvent) -> None: ...

    def list(self) -> Iterable[TimelineEvent]: ...


class IntegrationBus(Protocol):
    def publish(self, kind: str, payload: Dict[str, str]) -> None: ...
