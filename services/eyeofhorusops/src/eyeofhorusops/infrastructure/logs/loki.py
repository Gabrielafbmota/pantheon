from __future__ import annotations

import os
from typing import Dict, List, Optional

import time
import httpx

from eyeofhorusops.domain.contracts import LogSink


class LokiLogSink(LogSink):
    def __init__(self, url: str | None = None) -> None:
        self.base_url = url or os.getenv("LOKI_URL", "http://localhost:3100")
        self.client = httpx.Client(timeout=5.0)
        self._fallback: list[Dict[str, str]] = []

    def ingest(self, service_id: str, record: Dict[str, str]) -> None:
        labels = {
            "service_id": service_id,
            "env": record.get("env") or "",
            "level": record.get("level") or "",
            "trace_id": record.get("trace_id") or "",
            "correlation_id": record.get("correlation_id") or "",
            "container_name": record.get("container_name") or "",
        }
        label_str = ",".join([f'{k}="{v}"' for k, v in labels.items() if v])
        line = record.get("message", "")
        extra = record.get("extra") or {}
        payload = {
            "streams": [
                {
                    "stream": labels,
                    "values": [
                        [
                            str(int(time.time() * 1e9)),
                            line + (" " + str(extra) if extra else ""),
                        ]
                    ],
                }
            ]
        }
        try:
            resp = self.client.post(f"{self.base_url}/loki/api/v1/push", json=payload)
            resp.raise_for_status()
        except Exception:
            # Hardened: keep a local fallback copy to avoid data loss
            self._fallback.append({"stream": labels, "line": line})

    def search(
        self,
        service_id: Optional[str] = None,
        env: Optional[str] = None,
        level: Optional[str] = None,
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, str]]:
        selectors = []
        if service_id:
            selectors.append(f'service_id="{service_id}"')
        if env:
            selectors.append(f'env="{env}"')
        if level:
            selectors.append(f'level="{level}"')
        if trace_id:
            selectors.append(f'trace_id="{trace_id}"')
        if correlation_id:
            selectors.append(f'correlation_id="{correlation_id}"')
        selector = "{" + ",".join(selectors) + "}"
        params = {"query": selector, "limit": str(limit)}
        results: List[Dict[str, str]] = []
        try:
            resp = self.client.get(f"{self.base_url}/loki/api/v1/query", params=params)
            resp.raise_for_status()
            data = resp.json()
            for result in data.get("data", {}).get("result", []):
                stream = result.get("stream", {})
                for value in result.get("values", []):
                    results.append(
                        {
                            "service_id": stream.get("service_id"),
                            "env": stream.get("env"),
                            "level": stream.get("level"),
                            "trace_id": stream.get("trace_id"),
                            "correlation_id": stream.get("correlation_id"),
                            "container_name": stream.get("container_name"),
                            "message": value[1],
                        }
                    )
        except Exception:
            # Fall back to local buffer if Loki unavailable
            for item in self._fallback:
                if service_id and item["stream"].get("service_id") != service_id:  # type: ignore[index]
                    continue
                results.append(
                    {
                        "service_id": item["stream"].get("service_id"),  # type: ignore[index]
                        "env": item["stream"].get("env"),  # type: ignore[index]
                        "level": item["stream"].get("level"),  # type: ignore[index]
                        "trace_id": item["stream"].get("trace_id"),  # type: ignore[index]
                        "correlation_id": item["stream"].get("correlation_id"),  # type: ignore[index]
                        "container_name": item["stream"].get("container_name"),  # type: ignore[index]
                        "message": item["line"],
                    }
                )
        return results
