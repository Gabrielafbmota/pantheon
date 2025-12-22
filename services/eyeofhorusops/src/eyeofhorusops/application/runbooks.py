from __future__ import annotations

import time
from typing import Dict, Iterable, Optional

from eyeofhorusops.domain.contracts import (
    AuditLog,
    IncidentRepository,
    IntegrationBus,
    RunbookRepository,
    ServiceRepository,
)
from eyeofhorusops.domain.entities import (
    IncidentStatus,
    RemediationJob,
    RemediationStatus,
    RunbookAction,
    TimelineEvent,
    new_id,
    now_utc,
)


class RunbookService:
    def __init__(
        self,
        actions: RunbookRepository,
        incidents: IncidentRepository,
        services: ServiceRepository,
        audit_log: AuditLog | None = None,
        integrations: IntegrationBus | None = None,
    ) -> None:
        self.actions = actions
        self.incidents = incidents
        self.services = services
        self.audit_log = audit_log
        self.integrations = integrations

    def register_action(self, action: RunbookAction) -> RunbookAction:
        self.actions.add_action(action)
        return action

    def list_actions(self) -> Iterable[RunbookAction]:
        return self.actions.list_actions()

    def execute(
        self,
        service_id: str,
        incident_id: str,
        action_id: str,
        params: Dict[str, str],
        actor: str,
        correlation_id: Optional[str] = None,
    ) -> RemediationJob:
        service = self.services.get(service_id)
        if not service:
            raise ValueError(f"service_id={service_id} not registered")

        incident = self.incidents.get(incident_id)
        if not incident:
            raise ValueError(f"incident_id={incident_id} not found")

        action = self.actions.get_action(action_id)
        if not action:
            raise ValueError(f"action_id={action_id} not allowlisted")

        # Validate params
        for key in params.keys():
            if key not in action.allowed_params:
                raise ValueError(f"param {key} not allowed for action {action_id}")

        # Enforce cooldown per service+action
        if not self._cooldown_ok(service_id, action, correlation_id):
            job = RemediationJob(
                id=new_id(),
                incident_id=incident_id,
                action_id=action_id,
                service_id=service_id,
                params=params,
                actor=actor,
                correlation_id=correlation_id,
                status=RemediationStatus.BLOCKED,
                output="cooldown_in_effect",
            )
            self.actions.save_job(job)
            incident.add_event(
                TimelineEvent(
                    message=f"Runbook {action_id} blocked by cooldown",
                    actor=actor,
                    event_type="runbook_blocked",
                    correlation_id=correlation_id,
                )
            )
            self.incidents.save(incident)
            self._record_integration("runbook.cooldown_blocked", job)
            return job

        if action.requires_approval:
            job = RemediationJob(
                id=new_id(),
                incident_id=incident_id,
                action_id=action_id,
                service_id=service_id,
                params=params,
                actor=actor,
                correlation_id=correlation_id,
                status=RemediationStatus.BLOCKED,
                output="awaiting_approval",
            )
            self.actions.save_job(job)
            incident.add_event(
                TimelineEvent(
                    message=f"Runbook {action_id} pending approval",
                    actor=actor,
                    event_type="runbook_pending",
                    correlation_id=correlation_id,
                )
            )
            self.incidents.save(incident)
            self._record_integration("runbook.awaiting_approval", job)
            return job

        # Execute (MVP: simulated no-op)
        job = RemediationJob(
            id=new_id(),
            incident_id=incident_id,
            action_id=action_id,
            service_id=service_id,
            params=params,
            actor=actor,
            correlation_id=correlation_id,
        )
        job.mark_started()
        time.sleep(0)  # placeholder for execution latency
        job.mark_completed(output="noop-executed")
        self.actions.save_job(job)

        incident.add_event(
            TimelineEvent(
                message=f"Runbook {action_id} executed by {actor}",
                actor=actor,
                event_type="runbook_executed",
                correlation_id=correlation_id,
            )
        )
        # Automatically move to monitoring if previously mitigating
        if incident.status == IncidentStatus.MITIGATING:
            incident.status = IncidentStatus.MONITORING
        self.incidents.save(incident)
        self._record_integration("runbook.executed", job)
        return job

    def approve(self, job_id: str, approver: str, note: str = "") -> RemediationJob:
        job = self.actions.get_job(job_id)
        if not job:
            raise ValueError(f"job_id={job_id} not found")
        if job.status != RemediationStatus.BLOCKED or job.output != "awaiting_approval":
            raise ValueError("job not awaiting approval")

        job.mark_started()
        time.sleep(0)
        job.mark_completed(output="approved-noop")
        self.actions.save_job(job)

        incident = self.incidents.get(job.incident_id)
        if incident:
            incident.add_event(
                TimelineEvent(
                    message=f"Runbook {job.action_id} approved by {approver}. {note}",
                    actor=approver,
                    event_type="runbook_approved",
                    correlation_id=job.correlation_id,
                )
            )
            self.incidents.save(incident)
        self._record_integration("runbook.approved", job)
        return job

    def _cooldown_ok(self, service_id: str, action: RunbookAction, correlation_id: Optional[str]) -> bool:
        cooldown_seconds = action.cooldown_seconds
        if cooldown_seconds <= 0:
            return True
        now_ts = now_utc().timestamp()
        for job in self.actions.list_jobs():
            if job.service_id == service_id and job.action_id == action.id and job.finished_at:
                elapsed = now_ts - job.finished_at.timestamp()
                if elapsed < cooldown_seconds:
                    return False
        return True

    def _record_integration(self, kind: str, job: RemediationJob) -> None:
        if self.audit_log:
            self.audit_log.record(
                TimelineEvent(
                    message=f"{kind} for job {job.id}",
                    actor="system",
                    event_type=kind,
                    correlation_id=job.correlation_id,
                )
            )
        if self.integrations:
            self.integrations.publish(
                kind,
                {
                    "job_id": job.id,
                    "service_id": job.service_id,
                    "incident_id": job.incident_id,
                    "action_id": job.action_id,
                    "status": job.status.value,
                },
            )
