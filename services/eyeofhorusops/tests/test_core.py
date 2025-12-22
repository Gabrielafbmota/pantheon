from eyeofhorusops.application.incidents import IncidentService
from eyeofhorusops.application.logs import LogService
from eyeofhorusops.application.runbooks import RunbookService
from eyeofhorusops.application.service_registry import ServiceRegistry
from eyeofhorusops.domain.entities import Environment, IncidentStatus, RemediationStatus, RunbookAction, Service, Signal, SignalType
from eyeofhorusops.infrastructure.in_memory import (
    InMemoryAuditLog,
    InMemoryIncidentRepository,
    InMemoryIntegrationBus,
    InMemoryLogSink,
    InMemoryRunbookRepository,
    InMemoryServiceRepository,
)


def build_components():
    services = InMemoryServiceRepository()
    logs = InMemoryLogSink()
    incidents = InMemoryIncidentRepository()
    runbooks = InMemoryRunbookRepository()
    audit = InMemoryAuditLog()
    integration = InMemoryIntegrationBus()

    return {
        "services": services,
        "logs": logs,
        "incidents": incidents,
        "runbooks": runbooks,
        "audit": audit,
        "integration": integration,
        "registry": ServiceRegistry(repository=services, audit_log=audit, integrations=integration),
        "log_service": LogService(sink=logs, services=services, audit_log=audit, integrations=integration),
        "incident_service": IncidentService(
            incidents=incidents, services=services, audit_log=audit, integrations=integration
        ),
        "runbook_service": RunbookService(
            actions=runbooks, incidents=incidents, services=services, audit_log=audit, integrations=integration
        ),
    }


def test_service_registry_and_logs():
    c = build_components()
    registry = c["registry"]
    log_service = c["log_service"]

    svc = Service(id="svc-1", name="payments", env=Environment.PROD, owners=["sre@acme"])
    registry.register(svc)

    # unknown service should fail
    try:
        log_service.ingest("unknown", {"message": "test"})
        assert False, "expected failure for unknown service"
    except ValueError:
        pass

    log_service.ingest("svc-1", {"message": "container restarted", "level": "warn", "trace_id": "t-1"})
    results = log_service.search(service_id="svc-1", trace_id="t-1")
    assert len(results) == 1
    assert results[0]["message"] == "container restarted"


def test_incident_manual_and_from_signal():
    c = build_components()
    registry = c["registry"]
    incident_service = c["incident_service"]

    registry.register(Service(id="svc-1", name="payments", env=Environment.PROD, owners=[]))

    manual = incident_service.create_manual(
        service_id="svc-1",
        severity="sev1",
        summary="latencia alta",
        actor="oncall",
        correlation_id="corr-1",
    )
    assert manual.status == IncidentStatus.OPEN
    assert len(manual.timeline) == 1

    signal = Signal(
        service_id="svc-1",
        type=SignalType.ALERT,
        message="error rate spike",
        severity="sev1",
        trace_id="t-1",
        correlation_id="corr-1",
    )
    from_signal = incident_service.create_from_signal(signal)
    assert len(from_signal.signals) == 1
    assert from_signal.signals[0].message == "error rate spike"


def test_runbook_cooldown_and_approval():
    c = build_components()
    registry = c["registry"]
    incident_service = c["incident_service"]
    runbook_service = c["runbook_service"]

    registry.register(Service(id="svc-1", name="payments", env=Environment.PROD, owners=[]))
    incident = incident_service.create_manual(
        service_id="svc-1",
        severity="sev1",
        summary="db down",
        actor="oncall",
    )

    action = RunbookAction(
        id="restart",
        name="Restart service",
        description="noop restart",
        allowed_params=["reason"],
        cooldown_seconds=300,
    )
    runbook_service.register_action(action)

    job1 = runbook_service.execute(
        service_id="svc-1",
        incident_id=incident.id,
        action_id="restart",
        params={"reason": "recover"},
        actor="oncall",
    )
    assert job1.status.name == "COMPLETED"

    # Second execution blocked by cooldown
    job2 = runbook_service.execute(
        service_id="svc-1",
        incident_id=incident.id,
        action_id="restart",
        params={"reason": "recover"},
        actor="oncall",
    )
    assert job2.status.name == "BLOCKED"
    assert job2.output == "cooldown_in_effect"

    # Action requiring approval
    approval_action = RunbookAction(
        id="drain",
        name="Drain traffic",
        description="requires approval",
        allowed_params=[],
        cooldown_seconds=0,
        requires_approval=True,
    )
    runbook_service.register_action(approval_action)
    job3 = runbook_service.execute(
        service_id="svc-1",
        incident_id=incident.id,
        action_id="drain",
        params={},
        actor="oncall",
    )
    assert job3.status.name == "BLOCKED"
    assert job3.output == "awaiting_approval"
    approved = runbook_service.approve(job_id=job3.id, approver="admin")
    assert approved.status == RemediationStatus.COMPLETED
