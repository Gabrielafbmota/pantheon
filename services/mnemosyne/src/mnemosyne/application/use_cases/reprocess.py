from __future__ import annotations

from typing import List

from mnemosyne.application.use_cases.ingest import IngestionPipeline, IngestionRequest, IngestionResult
from mnemosyne.infrastructure.persistence.repository import KnowledgeRepository


class ReprocessIngestionUseCase:
    def __init__(self, repository: KnowledgeRepository, pipeline: IngestionPipeline) -> None:
        self.repository = repository
        self.pipeline = pipeline

    def execute(self, run_id: str) -> List[IngestionResult]:
        stored_run = self.repository.get_run(run_id)
        if not stored_run:
            raise ValueError(f"run_id {run_id} not found")
        inputs = [
            IngestionRequest(
                external_id=doc.external_id,
                source=doc.source,
                content=doc.content,
                tags=doc.tags,
                taxonomy=doc.taxonomy,
                manual_summary=doc.manual_summary,
                run_id=run_id,
            )
            for doc in stored_run.get("inputs", [])
        ]
        return self.pipeline.run(inputs)
