from __future__ import annotations

from mnemosyne.application.use_cases.ingest import IngestionPipeline
from mnemosyne.domain.contracts import KnowledgeRepository


class ReprocessIngestionUseCase:
    def __init__(self, repository: KnowledgeRepository, pipeline: IngestionPipeline) -> None:
        self.repository = repository
        self.pipeline = pipeline

    def execute(self, run_id: str):
        run = self.repository.get_run(run_id)
        if not run:
            raise ValueError(f"run_id={run_id} not found")
        return self.pipeline.run(run.requests)
