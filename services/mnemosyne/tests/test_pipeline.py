from mnemosyne.application.use_cases.ingest import IngestionPipeline, IngestionRequest
from mnemosyne.application.use_cases.reprocess import ReprocessIngestionUseCase
from mnemosyne.application.use_cases.search import SearchKnowledgeUseCase
from mnemosyne.domain.entities.models import Source, SourceType, Tag
from mnemosyne.infrastructure.indexing.simple_index import SimpleTextIndex
from mnemosyne.infrastructure.indexing.mongo_index import MongoTextIndex
from mnemosyne.infrastructure.persistence.in_memory import InMemoryKnowledgeRepository
from mnemosyne.infrastructure.persistence.mongo import MongoKnowledgeRepository
from mnemosyne.infrastructure.storage.s3 import S3RawDocumentStorage


def build_pipeline():
    repository = InMemoryKnowledgeRepository()
    index = SimpleTextIndex()
    pipeline = IngestionPipeline(repository=repository, index=index)
    search = SearchKnowledgeUseCase(repository=repository, index=index)
    reprocess = ReprocessIngestionUseCase(repository=repository, pipeline=pipeline)
    return repository, pipeline, search, reprocess


def test_deduplication_and_versioning():
    repo, pipeline, _, _ = build_pipeline()
    source = Source(id="aegis-1", name="Aegis", type=SourceType.AEGIS)
    doc = IngestionRequest(external_id="1", source=source, content="Incident A", tags=[Tag(key="sev1")], taxonomy=["incidents"])

    first_run = pipeline.run([doc])
    second_run = pipeline.run([doc])  # same fingerprint should deduplicate
    assert first_run[0].entry_id == second_run[0].entry_id
    assert second_run[0].deduplicated is True

    updated_doc = IngestionRequest(external_id="1", source=source, content="Incident A - patched", tags=[Tag(key="sev1")], taxonomy=["incidents"])
    third_run = pipeline.run([updated_doc])
    entry = next(iter(repo.list_entries()))
    assert len(entry.versions) == 2
    assert third_run[0].deduplicated is False


def test_search_with_filters():
    _, pipeline, search, _ = build_pipeline()
    source_ops = Source(id="ops-1", name="Ops", type=SourceType.EYE_OF_HORUS_OPS)
    source_adr = Source(id="adr-1", name="ADR", type=SourceType.ATLAS_FORGE)

    pipeline.run([
        IngestionRequest(
            external_id="inc-1",
            source=source_ops,
            content="Outage due to DB migration",
            tags=[Tag(key="sev1")],
            taxonomy=["incidents", "postmortem"],
        ),
        IngestionRequest(
            external_id="adr-1",
            source=source_adr,
            content="ADR: switch to MongoDB",
            tags=[Tag(key="architecture")],
            taxonomy=["adr"],
        ),
    ])

    results = search.execute(text="outage", source_types=[SourceType.EYE_OF_HORUS_OPS.value])
    assert len(results) == 1
    assert results[0].source.type == SourceType.EYE_OF_HORUS_OPS

    tag_filtered = search.execute(tags=["architecture"])
    assert len(tag_filtered) == 1
    assert tag_filtered[0].source.type == SourceType.ATLAS_FORGE


def test_reprocess_is_idempotent():
    repo, pipeline, _, reprocess = build_pipeline()
    source = Source(id="aegis-1", name="Aegis", type=SourceType.AEGIS)
    run_id = "run-123"
    doc = IngestionRequest(
        external_id="42",
        source=source,
        content="Aegis report with remediation",
        tags=[Tag(key="aegis")],
        taxonomy=["reports"],
        run_id=run_id,
    )

    first = pipeline.run([doc])
    second = reprocess.execute(run_id)
    assert first[0].entry_id == second[0].entry_id
    # ensure idempotent: reprocess should not create extra versions
    entry = next(iter(repo.list_entries()))
    assert len(entry.versions) == 1


class FakeCollection:
    def __init__(self):
        self.docs = {}

    def create_index(self, *args, **kwargs):
        return None

    def update_one(self, filter_doc, update_doc, upsert=False):
        _id = filter_doc.get("id") or filter_doc.get("entry_id") or filter_doc.get("run_id")
        if not _id:
            raise ValueError("id required")
        set_doc = update_doc.get("$set", update_doc)
        self.docs[_id] = set_doc

    def find_one(self, filter_doc):
        _id = filter_doc.get("id") or filter_doc.get("entry_id") or filter_doc.get("run_id")
        return self.docs.get(_id)

    def insert_many(self, docs):
        for doc in docs:
            key = doc.get("id") or doc.get("entry_id") or doc.get("run_id") or len(self.docs)
            self.docs[str(key)] = doc

    def find(self, filter_doc=None):
        if not filter_doc:
            return list(self.docs.values())
        results = []
        for doc in self.docs.values():
            match = True
            for k, v in filter_doc.items():
                if isinstance(v, dict) and "$in" in v:
                    if doc.get(k) not in v["$in"]:
                        match = False
                        break
                elif doc.get(k) != v:
                    match = False
                    break
            if match:
                results.append(doc)
        return results


class FakeDB:
    def __init__(self):
        self.collections = {}

    def __getitem__(self, item):
        if item not in self.collections:
            self.collections[item] = FakeCollection()
        return self.collections[item]


class FakeMongoClient:
    def __init__(self):
        self.dbs = {}

    def __getitem__(self, name):
        if name not in self.dbs:
            self.dbs[name] = FakeDB()
        return self.dbs[name]


def test_mongo_repository_and_index():
    client = FakeMongoClient()
    repo = MongoKnowledgeRepository(client=client)
    index = MongoTextIndex(client["mnemosyne"]["index"])
    pipeline = IngestionPipeline(repository=repo, index=index)

    source = Source(id="aegis-1", name="Aegis", type=SourceType.AEGIS)
    pipeline.run([IngestionRequest(external_id="1", source=source, content="DB outage in prod", tags=[Tag(key="sev1")])])

    entry = repo.get_entry("aegis-1:1")
    assert entry and entry.latest_version
    results = index.search(text="outage", source_types=[SourceType.AEGIS.value])
    assert entry.id in results
    run_id = next(iter(repo._runs.docs.keys()))  # type: ignore[attr-defined]
    assert repo.get_run(run_id) is not None


def test_s3_storage_is_used(monkeypatch):
    stored = {}

    class FakeS3:
        def put_object(self, Bucket, Key, Body):
            stored[(Bucket, Key)] = Body

    storage = S3RawDocumentStorage(bucket="bucket", client=FakeS3())
    repo, pipeline, _, _ = build_pipeline()
    pipeline.storage = storage
    source = Source(id="ops", name="Ops", type=SourceType.EYE_OF_HORUS_OPS)
    result = pipeline.run(
        [IngestionRequest(external_id="abc", source=source, content="raw data", taxonomy=["incidents"])]
    )[0]
    assert result.entry_id == "ops:abc"
    assert stored  # content written
    entry = next(iter(repo.list_entries()))
    assert entry.latest_version and entry.latest_version.raw_uri.endswith("abc.txt")
