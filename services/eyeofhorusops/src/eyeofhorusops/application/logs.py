from __future__ import annotations

from typing import Dict, List, Optional

from eyeofhorusops.domain.contracts import AuditLog, IntegrationBus, LogSink, ServiceRepository
from eyeofhorusops.domain.entities import Service, TimelineEvent


class LogService:
    def __init__(
        self,
        sink: LogSink,
        services: ServiceRepository,
        audit_log: AuditLog | None = None,
        integrations: IntegrationBus | None = None,
    ) -> None:
        self.sink = sink
        self.services = services
        self.audit_log = audit_log
        self.integrations = integrations

    def ingest(self, service_id: str, record: Dict[str, str]) -> None:
        if not self.services.get(service_id):
            raise ValueError(f"service_id={service_id} not registered")
        self.sink.ingest(service_id, record)
        if self.audit_log:
            self.audit_log.record(
                TimelineEvent(
                    message=f"log ingested for {service_id}",
                    actor=record.get("actor") or "system",
                    event_type="log_ingested",
                    correlation_id=record.get("correlation_id"),
                    trace_id=record.get("trace_id"),
                )
            )
        if self.integrations:
            self.integrations.publish(
                "logs.ingested",
                {
                    "service_id": service_id,
                    "trace_id": record.get("trace_id", ""),
                    "correlation_id": record.get("correlation_id", ""),
                },
            )

    def search(
        self,
        service_id: Optional[str] = None,
        env: Optional[str] = None,
        level: Optional[str] = None,
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, str]]:
        return self.sink.search(
            service_id=service_id,
            env=env,
            level=level,
            trace_id=trace_id,
            correlation_id=correlation_id,
            limit=limit,
        )
