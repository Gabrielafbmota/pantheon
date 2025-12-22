from __future__ import annotations

import logging
import os
from typing import Optional

try:
    from opentelemetry import metrics, trace
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
except ImportError:  # pragma: no cover - fallback when otel not installed
    metrics = None  # type: ignore
    trace = None  # type: ignore
    OTLPMetricExporter = None  # type: ignore
    OTLPSpanExporter = None  # type: ignore
    MeterProvider = None  # type: ignore
    PeriodicExportingMetricReader = None  # type: ignore
    Resource = None  # type: ignore
    TracerProvider = None  # type: ignore
    BatchSpanProcessor = None  # type: ignore
    ConsoleSpanExporter = None  # type: ignore
    ConsoleMetricExporter = None  # type: ignore
    FastAPIInstrumentor = None  # type: ignore

logger = logging.getLogger(__name__)


class Observability:
    def __init__(self, service_name: str) -> None:
        if os.getenv("MNEMO_DISABLE_OTEL", "1") == "1" or not (metrics and trace and Resource):
            self.ingestions_counter = _NoopCounter()
            self.search_counter = _NoopCounter()
            return

        resource = Resource.create({"service.name": service_name})

        tracer_provider = TracerProvider(resource=resource)
        tracer_provider.add_span_processor(BatchSpanProcessor(_build_trace_exporter()))
        trace.set_tracer_provider(tracer_provider)

        metric_reader = PeriodicExportingMetricReader(_build_metric_exporter())
        meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        metrics.set_meter_provider(meter_provider)
        self.meter = metrics.get_meter(service_name)
        self.ingestions_counter = self.meter.create_counter(
            "mnemosyne.ingestions", description="Number of ingestions executed"
        )
        self.search_counter = self.meter.create_counter("mnemosyne.searches", description="Number of searches executed")

    def instrument_fastapi(self, app) -> None:
        if not FastAPIInstrumentor:  # pragma: no cover
            return
        try:
            FastAPIInstrumentor.instrument_app(app)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to instrument FastAPI: %s", exc)


class _NoopCounter:
    def add(self, *_args, **_kwargs):
        return None


def _build_trace_exporter():
    if not OTLPSpanExporter:
        return ConsoleSpanExporter()
    try:
        return OTLPSpanExporter()
    except Exception:  # pragma: no cover - fallback for offline/dev
        return ConsoleSpanExporter()


def _build_metric_exporter():
    if not OTLPMetricExporter:
        return ConsoleMetricExporter()
    try:
        return OTLPMetricExporter()
    except Exception:  # pragma: no cover - fallback for offline/dev
        return ConsoleMetricExporter()
