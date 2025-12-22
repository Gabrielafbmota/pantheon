from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Optional

from eyeofhorusops.domain.contracts import (
    AuditLog,
    IncidentRepository,
    IntegrationBus,
    LogSink,
    RunbookRepository,
    ServiceRepository,
)
from eyeofhorusops.domain.entities import Incident, RemediationJob, RunbookAction, Service, TimelineEvent


class InMemoryServiceRepository(ServiceRepository):
    def __init__(self) -> None:
        self._services: Dict[str, Service] = {}

    def upsert(self, service: Service) -> None:
        self._services[service.id] = service

    def get(self, service_id: str) -> Optional[Service]:
        return self._services.get(service_id)

    def list(self) -> Iterable[Service]:
        return list(self._services.values())


class InMemoryLogSink(LogSink):
    def __init__(self) -> None:
        self._logs: List[Dict[str, str]] = []

    def ingest(self, service_id: str, record: Dict[str, str]) -> None:
        record = {**record, "service_id": service_id}
        self._logs.append(record)

    def search(
        self,
        service_id: Optional[str] = None,
        env: Optional[str] = None,
        level: Optional[str] = None,
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, str]]:
        results: List[Dict[str, str]] = []
        for record in reversed(self._logs):
            if service_id and record.get("service_id") != service_id:
                continue
            if env and record.get("env") != env:
                continue
            if level and record.get("level") != level:
                continue
            if trace_id and record.get("trace_id") != trace_id:
                continue
            if correlation_id and record.get("correlation_id") != correlation_id:
                continue
            results.append(record)
            if len(results) >= limit:
                break
        return results


class InMemoryIncidentRepository(IncidentRepository):
    def __init__(self) -> None:
        self._incidents: Dict[str, Incident] = {}

    def save(self, incident: Incident) -> None:
        self._incidents[incident.id] = incident

    def get(self, incident_id: str) -> Optional[Incident]:
        return self._incidents.get(incident_id)

    def list(self) -> Iterable[Incident]:
        return list(self._incidents.values())


class InMemoryRunbookRepository(RunbookRepository):
    def __init__(self) -> None:
        self._actions: Dict[str, RunbookAction] = {}
        self._jobs: Dict[str, RemediationJob] = {}
        self._cooldowns: Dict[str, float] = defaultdict(float)

    def add_action(self, action: RunbookAction) -> None:
        self._actions[action.id] = action

    def get_action(self, action_id: str) -> Optional[RunbookAction]:
        return self._actions.get(action_id)

    def list_actions(self) -> Iterable[RunbookAction]:
        return list(self._actions.values())

    def save_job(self, job: RemediationJob) -> None:
        self._jobs[job.id] = job

    def get_job(self, job_id: str) -> Optional[RemediationJob]:
        return self._jobs.get(job_id)

    def list_jobs(self) -> Iterable[RemediationJob]:
        return list(self._jobs.values())

    @property
    def cooldowns(self) -> Dict[str, float]:
        return self._cooldowns


class InMemoryAuditLog(AuditLog):
    def __init__(self) -> None:
        self._events: List[TimelineEvent] = []

    def record(self, event: TimelineEvent) -> None:
        self._events.append(event)

    def list(self) -> Iterable[TimelineEvent]:
        return list(self._events)


class InMemoryIntegrationBus(IntegrationBus):
    def __init__(self) -> None:
        self.events: List[Dict[str, str]] = []

    def publish(self, kind: str, payload: Dict[str, str]) -> None:
        self.events.append({"kind": kind, **payload})
