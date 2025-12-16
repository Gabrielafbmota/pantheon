from __future__ import annotations

from fastapi import FastAPI, HTTPException

from mnemosyne.application.use_cases.ingest import IngestionPipeline, IngestionRequest
from mnemosyne.application.use_cases.reprocess import ReprocessIngestionUseCase
from mnemosyne.application.use_cases.search import SearchKnowledgeUseCase
from mnemosyne.infrastructure.indexing.simple_index import SimpleTextIndex
from mnemosyne.infrastructure.persistence.in_memory import InMemoryKnowledgeRepository

app = FastAPI(title="Mnemosyne", version="0.1.0")
repository = InMemoryKnowledgeRepository()
index = SimpleTextIndex()
pipeline = IngestionPipeline(repository=repository, index=index)
search_use_case = SearchKnowledgeUseCase(repository=repository, index=index)
reprocess_use_case = ReprocessIngestionUseCase(repository=repository, pipeline=pipeline)


@app.post("/ingestions")
def ingest(documents: list[IngestionRequest]):
    return pipeline.run(documents)


@app.get("/search")
def search(text: str | None = None, tags: str | None = None, source_types: str | None = None, taxonomy: str | None = None):
    tag_list = tags.split(",") if tags else None
    source_type_list = source_types.split(",") if source_types else None
    taxonomy_list = taxonomy.split(",") if taxonomy else None
    return search_use_case.execute(text=text, tags=tag_list, source_types=source_type_list, taxonomy=taxonomy_list)


@app.post("/reprocess/{run_id}")
def reprocess(run_id: str):
    try:
        return reprocess_use_case.execute(run_id)
    except ValueError as exc:  # pragma: no cover - FastAPI handles response
        raise HTTPException(status_code=404, detail=str(exc))
