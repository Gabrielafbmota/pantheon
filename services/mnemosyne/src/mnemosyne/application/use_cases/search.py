from __future__ import annotations

from typing import List, Optional

from mnemosyne.domain.contracts import KnowledgeRepository, TextIndex
from mnemosyne.domain.entities.models import KnowledgeEntry


class SearchKnowledgeUseCase:
    def __init__(self, repository: KnowledgeRepository, index: TextIndex) -> None:
        self.repository = repository
        self.index = index

    def execute(
        self,
        text: Optional[str] = None,
        tags: Optional[List[str]] = None,
        taxonomy: Optional[List[str]] = None,
        source_types: Optional[List[str]] = None,
    ) -> List[KnowledgeEntry]:
        entry_ids = self.index.search(text=text, tags=tags, taxonomy=taxonomy, source_types=source_types)
        results: List[KnowledgeEntry] = []
        for entry_id in entry_ids:
            entry = self.repository.get_entry(entry_id)
            if entry:
                results.append(entry)
        return results
