from __future__ import annotations

from typing import List, Optional

from mnemosyne.domain.entities.models import KnowledgeEntry
from mnemosyne.infrastructure.indexing.simple_index import SimpleTextIndex
from mnemosyne.infrastructure.persistence.repository import KnowledgeRepository


class SearchKnowledgeUseCase:
    def __init__(self, repository: KnowledgeRepository, index: SimpleTextIndex) -> None:
        self.repository = repository
        self.index = index

    def execute(
        self,
        text: Optional[str] = None,
        tags: Optional[List[str]] = None,
        source_types: Optional[List[str]] = None,
        taxonomy: Optional[List[str]] = None,
    ) -> List[KnowledgeEntry]:
        if text:
            indexed_ids = set(self.index.search(text))
            candidates = [entry for entry in self.repository.list_entries() if entry.entry_id in indexed_ids]
        else:
            candidates = list(self.repository.list_entries())

        filtered: List[KnowledgeEntry] = []
        for entry in candidates:
            if source_types and entry.source.type.value not in source_types:
                continue
            if tags:
                tag_keys = {tag.key for tag in entry.tags}
                if not set(tags).issubset(tag_keys):
                    continue
            if taxonomy and not set(taxonomy).issubset(set(entry.taxonomy)):
                continue
            if text:
                latest = entry.latest_version
                if not latest:
                    continue
                text_lower = text.lower()
                if text_lower not in latest.content.lower() and text_lower not in latest.summary.lower():
                    continue
            filtered.append(entry)
        return filtered
