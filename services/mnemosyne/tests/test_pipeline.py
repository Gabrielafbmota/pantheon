from mnemosyne.application.use_cases.ingest import IngestionPipeline, IngestionRequest
from mnemosyne.application.use_cases.reprocess import ReprocessIngestionUseCase
from mnemosyne.application.use_cases.search import SearchKnowledgeUseCase
from mnemosyne.domain.entities.models import Source, SourceType, Tag
from mnemosyne.infrastructure.indexing.simple_index import SimpleTextIndex
from mnemosyne.infrastructure.persistence.in_memory import InMemoryKnowledgeRepository


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
