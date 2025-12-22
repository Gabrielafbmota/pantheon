from __future__ import annotations

import os

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from eyeofhorusops.application.health import HealthService
from eyeofhorusops.application.incidents import IncidentService
from eyeofhorusops.application.logs import LogService
from eyeofhorusops.application.runbooks import RunbookService
from eyeofhorusops.application.service_registry import ServiceRegistry
from eyeofhorusops.domain.entities import (
    Environment,
    IncidentStatus,
    RunbookAction,
    Service,
    Signal,
    SignalType,
    TimelineEvent,
)
from eyeofhorusops.infrastructure.in_memory import (
    InMemoryIncidentRepository,
    InMemoryLogSink,
    InMemoryIntegrationBus,
    InMemoryRunbookRepository,
    InMemoryServiceRepository,
    InMemoryAuditLog,
)
from eyeofhorusops.infrastructure.logs.loki import LokiLogSink
from eyeofhorusops.infrastructure.observability import Observability
from eyeofhorusops.infrastructure.persistence.mongo import (
    MongoIncidentRepository,
    MongoRunbookRepository,
    MongoServiceRepository,
)

app = FastAPI(title="EyeOfHorusOps", version="0.1.1")
observability = Observability(service_name="eyeofhorusops")
observability.instrument_fastapi(app)


# Dependency wiring (Mongo + Loki by default; fallback to in-memory with EYEOPS_PERSISTENCE=memory or failures)
persistence = os.getenv("EYEOPS_PERSISTENCE", "mongo").lower()
audit_log = InMemoryAuditLog()
integration_bus = InMemoryIntegrationBus()

try:
    if persistence == "memory":
        raise RuntimeError("memory requested")
    service_repo = MongoServiceRepository()
    incident_repo = MongoIncidentRepository()
    log_sink = LokiLogSink()
    runbook_repo = MongoRunbookRepository()
except Exception:
    service_repo = InMemoryServiceRepository()
    incident_repo = InMemoryIncidentRepository()
    log_sink = InMemoryLogSink()
    runbook_repo = InMemoryRunbookRepository()
    persistence = "memory"

registry = ServiceRegistry(repository=service_repo, audit_log=audit_log, integrations=integration_bus)
log_service = LogService(sink=log_sink, services=service_repo, audit_log=audit_log, integrations=integration_bus)
health_service = HealthService(services=service_repo)
incident_service = IncidentService(
    incidents=incident_repo,
    services=service_repo,
    audit_log=audit_log,
    integrations=integration_bus,
)
runbook_service = RunbookService(
    actions=runbook_repo,
    incidents=incident_repo,
    services=service_repo,
    audit_log=audit_log,
    integrations=integration_bus,
)


class AuthContext(BaseModel):
    actor: str
    roles: list[str] = Field(default_factory=list)


def get_auth(
    x_api_key: str | None = Header(default=None),
    x_actor: str | None = Header(default=None),
    x_roles: str | None = Header(default=None),
) -> AuthContext:
    configured = os.getenv("EYEOPS_API_KEY")
    if configured and x_api_key != configured:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid api key")
    roles = [r.strip().lower() for r in (x_roles or "").split(",") if r]
    return AuthContext(actor=x_actor or "anonymous", roles=roles)


def ensure_role(ctx: AuthContext, allowed: set[str]) -> None:
    if not allowed:
        return
    if not set(ctx.roles) & allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")


class ServiceIn(BaseModel):
    id: str
    name: str
    env: Environment = Environment.PROD
    owners: list[str] = Field(default_factory=list)
    logging_endpoint: str | None = None
    health_url: str | None = None
    tags: list[str] = Field(default_factory=list)
    otel_config: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, str] = Field(default_factory=dict)


class ServiceOut(ServiceIn):
    pass


class LogRecordIn(BaseModel):
    env: str | None = None
    level: str | None = None
    message: str
    trace_id: str | None = None
    correlation_id: str | None = None
    container_name: str | None = None
    extra: dict[str, str] = Field(default_factory=dict)


class IncidentCreate(BaseModel):
    service_id: str
    severity: str
    summary: str
    actor: str
    correlation_id: str | None = None
    trace_id: str | None = None


class SignalIn(BaseModel):
    service_id: str
    type: SignalType
    severity: str
    message: str
    trace_id: str | None = None
    correlation_id: str | None = None


class RunbookActionIn(BaseModel):
    id: str
    name: str
    description: str
    allowed_params: list[str] = Field(default_factory=list)
    cooldown_seconds: int = 0
    requires_approval: bool = False
    guardrails: dict[str, str] = Field(default_factory=dict)


class RunbookExecIn(BaseModel):
    service_id: str
    incident_id: str
    action_id: str
    params: dict[str, str] = Field(default_factory=dict)
    actor: str
    correlation_id: str | None = None


class RunbookApproval(BaseModel):
    job_id: str
    approver: str
    note: str | None = None


@app.get("/health")
def service_health():
    return {"status": "ok", "persistence": persistence}


@app.post("/services", response_model=ServiceOut)
def register_service(
    payload: ServiceIn,
    reg: ServiceRegistry = Depends(lambda: registry),
    ctx: AuthContext = Depends(get_auth),
) -> Service:
    ensure_role(ctx, {"ops", "admin"})
    service = Service(**payload.model_dump())
    return reg.register(service)


@app.get("/services", response_model=list[ServiceOut])
def list_services(reg: ServiceRegistry = Depends(lambda: registry), ctx: AuthContext = Depends(get_auth)):
    ensure_role(ctx, {"ops", "admin"})
    return list(reg.list())


@app.get("/services/{service_id}", response_model=ServiceOut)
def get_service(service_id: str, reg: ServiceRegistry = Depends(lambda: registry), ctx: AuthContext = Depends(get_auth)):
    ensure_role(ctx, {"ops", "admin"})
    service = reg.get(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="service not found")
    return service


@app.post("/logs/{service_id}")
def ingest_log(
    service_id: str,
    payload: LogRecordIn,
    logs: LogService = Depends(lambda: log_service),
    ctx: AuthContext = Depends(get_auth),
):
    ensure_role(ctx, {"ops", "service"})
    logs.ingest(service_id, payload.model_dump())
    observability.log_ingest_counter.add(1)
    return {"status": "accepted"}


@app.get("/logs")
def search_logs(
    service_id: str | None = None,
    env: str | None = None,
    level: str | None = None,
    trace_id: str | None = None,
    correlation_id: str | None = None,
    limit: int = 100,
    logs: LogService = Depends(lambda: log_service),
    ctx: AuthContext = Depends(get_auth),
):
    ensure_role(ctx, {"ops", "admin"})
    return logs.search(
        service_id=service_id,
        env=env,
        level=level,
        trace_id=trace_id,
        correlation_id=correlation_id,
        limit=limit,
    )


@app.get("/health/{service_id}")
def health(service_id: str, health_svc: HealthService = Depends(lambda: health_service)):
    return health_svc.check(service_id)


@app.post("/incidents")
def create_incident(
    payload: IncidentCreate,
    svc: IncidentService = Depends(lambda: incident_service),
    ctx: AuthContext = Depends(get_auth),
):
    ensure_role(ctx, {"ops"})
    incident = svc.create_manual(
        service_id=payload.service_id,
        severity=payload.severity,
        summary=payload.summary,
        actor=payload.actor or ctx.actor,
        correlation_id=payload.correlation_id,
        trace_id=payload.trace_id,
    )
    observability.incident_counter.add(1)
    return incident


@app.post("/alerts")
def create_incident_from_signal(
    payload: SignalIn, svc: IncidentService = Depends(lambda: incident_service), ctx: AuthContext = Depends(get_auth)
):
    ensure_role(ctx, {"ops"})
    signal = Signal(**payload.model_dump())
    incident = svc.create_from_signal(signal)
    observability.incident_counter.add(1)
    return incident


@app.get("/incidents")
def list_incidents(svc: IncidentService = Depends(lambda: incident_service), ctx: AuthContext = Depends(get_auth)):
    ensure_role(ctx, {"ops", "admin"})
    return list(svc.list())


@app.get("/incidents/{incident_id}")
def get_incident(incident_id: str, svc: IncidentService = Depends(lambda: incident_service), ctx: AuthContext = Depends(get_auth)):
    ensure_role(ctx, {"ops", "admin"})
    try:
        return svc.get(incident_id)
    except ValueError as exc:  # noqa: BLE001
        raise HTTPException(status_code=404, detail=str(exc)) from exc


class StatusChange(BaseModel):
    status: IncidentStatus
    note: str | None = None
    actor: str


@app.post("/incidents/{incident_id}/status")
def change_status(
    incident_id: str,
    payload: StatusChange,
    svc: IncidentService = Depends(lambda: incident_service),
    ctx: AuthContext = Depends(get_auth),
):
    ensure_role(ctx, {"ops"})
    return svc.transition(
        incident_id=incident_id,
        status=payload.status,
        actor=payload.actor,
        note=payload.note or "",
    )


@app.post("/runbooks/actions")
def register_action(
    payload: RunbookActionIn, svc: RunbookService = Depends(lambda: runbook_service), ctx: AuthContext = Depends(get_auth)
):
    ensure_role(ctx, {"admin"})
    action = RunbookAction(**payload.model_dump())
    return svc.register_action(action)


@app.get("/runbooks/actions")
def list_actions(svc: RunbookService = Depends(lambda: runbook_service), ctx: AuthContext = Depends(get_auth)):
    ensure_role(ctx, {"ops", "admin"})
    return list(svc.list_actions())


@app.post("/runbooks/execute")
def execute_runbook(
    payload: RunbookExecIn, svc: RunbookService = Depends(lambda: runbook_service), ctx: AuthContext = Depends(get_auth)
):
    ensure_role(ctx, {"ops"})
    try:
        job = svc.execute(
            service_id=payload.service_id,
            incident_id=payload.incident_id,
            action_id=payload.action_id,
            params=payload.params,
            actor=payload.actor or ctx.actor,
            correlation_id=payload.correlation_id,
        )
        observability.runbook_counter.add(1)
        return job
    except ValueError as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/runbooks/approve")
def approve_runbook(payload: RunbookApproval, svc: RunbookService = Depends(lambda: runbook_service), ctx: AuthContext = Depends(get_auth)):
    ensure_role(ctx, {"admin"})
    try:
        job = svc.approve(job_id=payload.job_id, approver=payload.approver, note=payload.note or "")
        observability.runbook_counter.add(1)
        return job
    except ValueError as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/metrics")
def metrics():
    return {
        "logs": getattr(log_service, "sink", None).__class__.__name__,
        "incidents": len(list(incident_service.list())),
        "runbook_jobs": len(list(runbook_service.actions.list_jobs())),
        "audit_events": len(list(audit_log.list())),
    }
