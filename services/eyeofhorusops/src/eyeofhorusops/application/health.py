from __future__ import annotations

from typing import Dict, Optional

import httpx

from eyeofhorusops.domain.contracts import ServiceRepository
from eyeofhorusops.domain.entities import Service


class HealthService:
    def __init__(self, services: ServiceRepository, timeout_seconds: float = 2.0) -> None:
        self.services = services
        self.timeout_seconds = timeout_seconds

    def check(self, service_id: str) -> Dict[str, str]:
        service = self.services.get(service_id)
        if not service:
            raise ValueError(f"service_id={service_id} not registered")

        if not service.health_url:
            return {"service_id": service_id, "status": "unknown", "detail": "health_url not configured"}

        try:
            response = httpx.get(service.health_url, timeout=self.timeout_seconds)
            status = "healthy" if response.status_code < 300 else "degraded"
            return {
                "service_id": service_id,
                "status": status,
                "http_status": str(response.status_code),
                "detail": response.text[:200],
            }
        except Exception as exc:  # noqa: BLE001
            return {"service_id": service_id, "status": "degraded", "detail": str(exc)}
