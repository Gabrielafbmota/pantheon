from __future__ import annotations

from typing import Iterable

from eyeofhorusops.domain.contracts import AuditLog, IntegrationBus, ServiceRepository
from eyeofhorusops.domain.entities import Service, TimelineEvent


class ServiceRegistry:
    def __init__(
        self,
        repository: ServiceRepository,
        audit_log: AuditLog | None = None,
        integrations: IntegrationBus | None = None,
    ) -> None:
        self.repository = repository
        self.audit_log = audit_log
        self.integrations = integrations

    def register(self, service: Service) -> Service:
        self.repository.upsert(service)
        if self.audit_log:
            self.audit_log.record(
                TimelineEvent(
                    message=f"service registered: {service.id}",
                    actor="system",
                    event_type="service_registered",
                )
            )
        if self.integrations:
            self.integrations.publish("service.registered", {"service_id": service.id, "env": service.env.value})
        return service

    def list(self) -> Iterable[Service]:
        return self.repository.list()

    def get(self, service_id: str) -> Service | None:
        return self.repository.get(service_id)
