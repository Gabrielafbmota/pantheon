from __future__ import annotations

from typing import Iterable, Optional

from eyeofhorusops.domain.contracts import AuditLog, IncidentRepository, IntegrationBus, ServiceRepository
from eyeofhorusops.domain.entities import (
    Incident,
    IncidentStatus,
    Signal,
    TimelineEvent,
    new_id,
    now_utc,
)


class IncidentService:
    def __init__(
        self,
        incidents: IncidentRepository,
        services: ServiceRepository,
        audit_log: AuditLog | None = None,
        integrations: IntegrationBus | None = None,
    ) -> None:
        self.incidents = incidents
        self.services = services
        self.audit_log = audit_log
        self.integrations = integrations

    def create_manual(
        self,
        service_id: str,
        severity: str,
        summary: str,
        actor: str,
        correlation_id: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> Incident:
        self._ensure_service(service_id)
        incident = Incident(
            id=new_id(),
            service_id=service_id,
            severity=severity,
            status=IncidentStatus.OPEN,
            summary=summary,
            correlation_id=correlation_id,
        )
        incident.add_event(
            TimelineEvent(
                message=f"Incident opened: {summary}",
                actor=actor,
                event_type="opened",
                correlation_id=correlation_id,
                trace_id=trace_id,
            )
        )
        self.incidents.save(incident)
        self._record_integration("incident.opened", incident)
        return incident

    def create_from_signal(self, signal: Signal, actor: str = "system") -> Incident:
        self._ensure_service(signal.service_id)
        incident = Incident(
            id=new_id(),
            service_id=signal.service_id,
            severity=signal.severity,
            status=IncidentStatus.OPEN,
            summary=signal.message,
            correlation_id=signal.correlation_id,
        )
        incident.add_signal(signal)
        incident.add_event(
            TimelineEvent(
                message=f"Incident created from signal: {signal.message}",
                actor=actor,
                event_type="signal",
                correlation_id=signal.correlation_id,
                trace_id=signal.trace_id,
            )
        )
        self.incidents.save(incident)
        self._record_integration("incident.signal", incident)
        return incident

    def transition(self, incident_id: str, status: IncidentStatus, actor: str, note: str = "") -> Incident:
        incident = self._get_or_throw(incident_id)
        incident.status = status
        incident.updated_at = now_utc()
        if note or status:
            incident.add_event(
                TimelineEvent(
                    message=f"Status changed to {status.value}. {note}",
                    actor=actor,
                    event_type="status_change",
                    correlation_id=incident.correlation_id,
                )
            )
        self.incidents.save(incident)
        self._record_integration("incident.status", incident)
        return incident

    def add_timeline(self, incident_id: str, event: TimelineEvent) -> Incident:
        incident = self._get_or_throw(incident_id)
        incident.add_event(event)
        self.incidents.save(incident)
        return incident

    def list(self) -> Iterable[Incident]:
        return self.incidents.list()

    def get(self, incident_id: str) -> Incident:
        return self._get_or_throw(incident_id)

    def _ensure_service(self, service_id: str) -> None:
        if not self.services.get(service_id):
            raise ValueError(f"service_id={service_id} not registered")

    def _get_or_throw(self, incident_id: str) -> Incident:
        incident = self.incidents.get(incident_id)
        if not incident:
            raise ValueError(f"incident_id={incident_id} not found")
        return incident

    def _record_integration(self, kind: str, incident: Incident) -> None:
        if self.audit_log:
            self.audit_log.record(
                TimelineEvent(
                    message=f"{kind} for incident {incident.id}",
                    actor="system",
                    event_type=kind,
                    correlation_id=incident.correlation_id,
                )
            )
        if self.integrations:
            self.integrations.publish(
                kind,
                {"incident_id": incident.id, "service_id": incident.service_id, "status": incident.status.value},
            )
