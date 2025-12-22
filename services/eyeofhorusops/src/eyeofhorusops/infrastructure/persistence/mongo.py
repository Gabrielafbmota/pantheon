from __future__ import annotations

import os
from datetime import datetime
from typing import Dict, Iterable, List, Optional

from pymongo import MongoClient
from pymongo.collection import Collection

from eyeofhorusops.domain.contracts import IncidentRepository, RunbookRepository, ServiceRepository
from eyeofhorusops.domain.entities import (
    Environment,
    Incident,
    IncidentStatus,
    RemediationJob,
    RemediationStatus,
    RunbookAction,
    Service,
    Signal,
    TimelineEvent,
    now_utc,
)


def _get_client() -> MongoClient:
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    return MongoClient(uri, serverSelectionTimeoutMS=2000, connectTimeoutMS=2000, retryWrites=False)


def _db_name() -> str:
    return os.getenv("MONGO_DB", "eyeofhorusops")


def _dt(value: datetime | None) -> datetime | None:
    return value if value is None else value


def _dt_from(value) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)


def _signal_to_dict(signal: Signal) -> Dict:
    return {
        "service_id": signal.service_id,
        "type": signal.type.value if hasattr(signal.type, "value") else signal.type,
        "message": signal.message,
        "severity": signal.severity,
        "trace_id": signal.trace_id,
        "correlation_id": signal.correlation_id,
        "timestamp": _dt(signal.timestamp),
        "attributes": signal.attributes,
    }


def _signal_from_dict(data: Dict) -> Signal:
    return Signal(
        service_id=data["service_id"],
        type=data["type"],
        message=data["message"],
        severity=data["severity"],
        trace_id=data.get("trace_id"),
        correlation_id=data.get("correlation_id"),
        timestamp=_dt_from(data.get("timestamp")) or now_utc(),
        attributes=data.get("attributes") or {},
    )


def _timeline_to_dict(evt: TimelineEvent) -> Dict:
    return {
        "message": evt.message,
        "actor": evt.actor,
        "event_type": evt.event_type,
        "timestamp": _dt(evt.timestamp),
        "correlation_id": evt.correlation_id,
        "trace_id": evt.trace_id,
    }


def _timeline_from_dict(data: Dict) -> TimelineEvent:
    return TimelineEvent(
        message=data["message"],
        actor=data["actor"],
        event_type=data["event_type"],
        timestamp=_dt_from(data.get("timestamp")) or now_utc(),
        correlation_id=data.get("correlation_id"),
        trace_id=data.get("trace_id"),
    )


class MongoServiceRepository(ServiceRepository):
    def __init__(self, client: MongoClient | None = None) -> None:
        client = client or _get_client()
        db = client[_db_name()]
        self.collection: Collection = db["services"]
        self.collection.create_index("id", unique=True)

    def upsert(self, service: Service) -> None:
        self.collection.update_one(
            {"id": service.id},
            {
                "$set": {
                    "id": service.id,
                    "name": service.name,
                    "env": service.env.value if hasattr(service.env, "value") else service.env,
                    "owners": service.owners,
                    "logging_endpoint": service.logging_endpoint,
                    "health_url": service.health_url,
                    "tags": service.tags,
                    "otel_config": service.otel_config,
                    "metadata": service.metadata,
                }
            },
            upsert=True,
        )

    def get(self, service_id: str) -> Optional[Service]:
        doc = self.collection.find_one({"id": service_id})
        if not doc:
            return None
        return self._from_doc(doc)

    def list(self) -> Iterable[Service]:
        return [self._from_doc(doc) for doc in self.collection.find({})]

    def _from_doc(self, doc: Dict) -> Service:
        return Service(
            id=doc["id"],
            name=doc["name"],
            env=Environment(doc.get("env", "other")),
            owners=doc.get("owners", []),
            logging_endpoint=doc.get("logging_endpoint"),
            health_url=doc.get("health_url"),
            tags=doc.get("tags", []),
            otel_config=doc.get("otel_config", {}),
            metadata=doc.get("metadata", {}),
        )


class MongoIncidentRepository(IncidentRepository):
    def __init__(self, client: MongoClient | None = None) -> None:
        client = client or _get_client()
        db = client[_db_name()]
        self.collection: Collection = db["incidents"]
        self.collection.create_index("id", unique=True)

    def save(self, incident: Incident) -> None:
        doc = {
            "id": incident.id,
            "service_id": incident.service_id,
            "severity": incident.severity,
            "status": incident.status.value if hasattr(incident.status, "value") else incident.status,
            "summary": incident.summary,
            "signals": [_signal_to_dict(s) for s in incident.signals],
            "timeline": [_timeline_to_dict(e) for e in incident.timeline],
            "runbook_refs": incident.runbook_refs,
            "created_at": _dt(incident.created_at),
            "updated_at": _dt(incident.updated_at),
            "correlation_id": incident.correlation_id,
        }
        self.collection.update_one({"id": incident.id}, {"$set": doc}, upsert=True)

    def get(self, incident_id: str) -> Optional[Incident]:
        doc = self.collection.find_one({"id": incident_id})
        if not doc:
            return None
        return self._from_doc(doc)

    def list(self) -> Iterable[Incident]:
        return [self._from_doc(doc) for doc in self.collection.find({})]

    def _from_doc(self, doc: Dict) -> Incident:
        return Incident(
            id=doc["id"],
            service_id=doc["service_id"],
            severity=doc["severity"],
            status=IncidentStatus(doc["status"]),
            summary=doc["summary"],
            signals=[_signal_from_dict(s) for s in doc.get("signals", [])],
            timeline=[_timeline_from_dict(e) for e in doc.get("timeline", [])],
            runbook_refs=doc.get("runbook_refs", []),
            created_at=_dt_from(doc.get("created_at")) or now_utc(),
            updated_at=_dt_from(doc.get("updated_at")) or now_utc(),
            correlation_id=doc.get("correlation_id"),
        )


class MongoRunbookRepository(RunbookRepository):
    def __init__(self, client: MongoClient | None = None) -> None:
        client = client or _get_client()
        db = client[_db_name()]
        self.actions: Collection = db["runbook_actions"]
        self.jobs: Collection = db["runbook_jobs"]
        self.actions.create_index("id", unique=True)
        self.jobs.create_index("id", unique=True)

    def add_action(self, action: RunbookAction) -> None:
        doc = {
            "id": action.id,
            "name": action.name,
            "description": action.description,
            "allowed_params": action.allowed_params,
            "cooldown_seconds": action.cooldown_seconds,
            "requires_approval": action.requires_approval,
            "guardrails": action.guardrails,
        }
        self.actions.update_one({"id": action.id}, {"$set": doc}, upsert=True)

    def get_action(self, action_id: str) -> Optional[RunbookAction]:
        doc = self.actions.find_one({"id": action_id})
        if not doc:
            return None
        return RunbookAction(
            id=doc["id"],
            name=doc["name"],
            description=doc["description"],
            allowed_params=doc.get("allowed_params", []),
            cooldown_seconds=doc.get("cooldown_seconds", 0),
            requires_approval=doc.get("requires_approval", False),
            guardrails=doc.get("guardrails", {}),
        )

    def list_actions(self) -> Iterable[RunbookAction]:
        return [
            RunbookAction(
                id=doc["id"],
                name=doc["name"],
                description=doc["description"],
                allowed_params=doc.get("allowed_params", []),
                cooldown_seconds=doc.get("cooldown_seconds", 0),
                requires_approval=doc.get("requires_approval", False),
                guardrails=doc.get("guardrails", {}),
            )
            for doc in self.actions.find({})
        ]

    def save_job(self, job: RemediationJob) -> None:
        doc = {
            "id": job.id,
            "incident_id": job.incident_id,
            "action_id": job.action_id,
            "service_id": job.service_id,
            "params": job.params,
            "actor": job.actor,
            "correlation_id": job.correlation_id,
            "status": job.status.value if hasattr(job.status, "value") else job.status,
            "started_at": _dt(job.started_at),
            "finished_at": _dt(job.finished_at),
            "output": job.output,
            "error": job.error,
        }
        self.jobs.update_one({"id": job.id}, {"$set": doc}, upsert=True)

    def get_job(self, job_id: str) -> Optional[RemediationJob]:
        doc = self.jobs.find_one({"id": job_id})
        if not doc:
            return None
        return self._from_doc(doc)

    def list_jobs(self) -> Iterable[RemediationJob]:
        return [self._from_doc(doc) for doc in self.jobs.find({})]

    def _from_doc(self, doc: Dict) -> RemediationJob:
        return RemediationJob(
            id=doc["id"],
            incident_id=doc["incident_id"],
            action_id=doc["action_id"],
            service_id=doc["service_id"],
            params=doc.get("params", {}),
            actor=doc.get("actor", "unknown"),
            correlation_id=doc.get("correlation_id"),
            status=RemediationStatus(doc.get("status", RemediationStatus.PENDING)),
            started_at=_dt_from(doc.get("started_at")),
            finished_at=_dt_from(doc.get("finished_at")),
            output=doc.get("output"),
            error=doc.get("error"),
        )
