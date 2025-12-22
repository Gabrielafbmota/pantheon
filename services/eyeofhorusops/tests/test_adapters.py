import json
from typing import Dict, List

import httpx
import pytest

from eyeofhorusops.domain.entities import Environment, Incident, RunbookAction, Service, Signal, SignalType, TimelineEvent
from eyeofhorusops.infrastructure.logs.loki import LokiLogSink
from eyeofhorusops.infrastructure.persistence.mongo import (
    MongoIncidentRepository,
    MongoRunbookRepository,
    MongoServiceRepository,
)


# --- Fakes for Mongo client/collection ---
class FakeCollection:
    def __init__(self) -> None:
        self.docs: Dict[str, Dict] = {}
        self.last_query = None

    def create_index(self, *args, **kwargs):
        return None

    def update_one(self, filter_doc: Dict, update_doc: Dict, upsert: bool = False):
        _id = filter_doc.get("id")
        if _id is None:
            raise ValueError("id required")
        set_doc = update_doc.get("$set", update_doc)
        self.docs[_id] = set_doc

    def find_one(self, filter_doc: Dict):
        _id = filter_doc.get("id")
        return self.docs.get(_id)

    def find(self, filter_doc: Dict | None = None):
        self.last_query = filter_doc
        return list(self.docs.values())


class FakeDB:
    def __init__(self) -> None:
        self.collections: Dict[str, FakeCollection] = {}

    def __getitem__(self, item: str) -> FakeCollection:
        if item not in self.collections:
            self.collections[item] = FakeCollection()
        return self.collections[item]


class FakeMongoClient:
    def __init__(self) -> None:
        self.dbs: Dict[str, FakeDB] = {}

    def __getitem__(self, name: str) -> FakeDB:
        if name not in self.dbs:
            self.dbs[name] = FakeDB()
        return self.dbs[name]


# --- Loki mock transport ---
class _Recorder:
    def __init__(self):
        self.requests: List[httpx.Request] = []


def _mock_transport(recorder: _Recorder):
    def handler(request: httpx.Request) -> httpx.Response:
        recorder.requests.append(request)
        if request.method == "POST":
            return httpx.Response(204)
        if request.method == "GET":
            # return a fake query response
            data = {
                "data": {
                    "result": [
                        {
                            "stream": {
                                "service_id": request.url.params.get("service_id") or "svc-1",
                                "env": "prod",
                                "level": "warn",
                                "trace_id": "t-1",
                                "correlation_id": "c-1",
                                "container_name": "app",
                            },
                            "values": [["0", "msg"]],
                        }
                    ]
                }
            }
            return httpx.Response(200, json=data)
        return httpx.Response(404)

    return httpx.MockTransport(handler)


def test_mongo_repositories_serialization():
    client = FakeMongoClient()
    services_repo = MongoServiceRepository(client=client)
    incidents_repo = MongoIncidentRepository(client=client)
    runbooks_repo = MongoRunbookRepository(client=client)

    service = Service(id="svc-1", name="payments", env=Environment.PROD, owners=["sre"])
    services_repo.upsert(service)
    fetched = services_repo.get("svc-1")
    assert fetched and fetched.name == "payments" and fetched.env == Environment.PROD

    incident = Incident(
        id="inc-1",
        service_id="svc-1",
        severity="sev1",
        status="open",
        summary="outage",
        signals=[
            Signal(
                service_id="svc-1",
                type=SignalType.ALERT,
                message="spike",
                severity="sev1",
            )
        ],
        timeline=[TimelineEvent(message="created", actor="oncall", event_type="opened")],
        runbook_refs=[],
    )
    incidents_repo.save(incident)
    loaded = incidents_repo.get("inc-1")
    assert loaded and loaded.summary == "outage"
    assert loaded.signals[0].message == "spike"
    assert loaded.timeline[0].actor == "oncall"

    action = RunbookAction(
        id="restart",
        name="Restart",
        description="restart svc",
        allowed_params=["reason"],
        cooldown_seconds=10,
    )
    runbooks_repo.add_action(action)
    assert runbooks_repo.get_action("restart") is not None


def test_loki_sink_push_and_query():
    recorder = _Recorder()
    transport = _mock_transport(recorder)
    sink = LokiLogSink(url="http://loki.test")
    sink.client = httpx.Client(transport=transport)

    sink.ingest("svc-1", {"message": "hello", "env": "prod", "level": "info", "trace_id": "t-1"})
    assert recorder.requests, "no request recorded"
    req = recorder.requests[0]
    body = json.loads(req.content)
    assert body["streams"][0]["stream"]["service_id"] == "svc-1"

    results = sink.search(service_id="svc-1", trace_id="t-1", limit=5)
    assert len(results) == 1
    assert results[0]["message"] == "msg"
