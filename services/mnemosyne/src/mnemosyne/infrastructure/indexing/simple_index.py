from __future__ import annotations

from typing import Dict, List, Optional, Set

from mnemosyne.domain.contracts import TextIndex
from mnemosyne.domain.entities.models import KnowledgeEntry


class SimpleTextIndex(TextIndex):
    def __init__(self) -> None:
        self._index: Dict[str, Dict[str, object]] = {}

    def index(self, entry: KnowledgeEntry) -> None:
        version = entry.latest_version
        if not version:
            return

        text_blob = f"{version.normalized_content}\n{version.summary}".lower()
        tags = {tag.key for tag in version.tags}
        taxonomy = set(version.taxonomy)
        self._index[entry.id] = {
            "text": text_blob,
            "tags": tags,
            "taxonomy": taxonomy,
            "source_type": entry.source.type.value,
        }

    def search(
        self,
        text: Optional[str] = None,
        tags: Optional[List[str]] = None,
        taxonomy: Optional[List[str]] = None,
        source_types: Optional[List[str]] = None,
    ) -> List[str]:
        query = (text or "").lower()
        tag_filter: Set[str] = set(tags or [])
        taxonomy_filter: Set[str] = set(taxonomy or [])
        source_filter: Set[str] = set(source_types or [])

        results: List[str] = []
        for entry_id, doc in self._index.items():
            if query and query not in doc["text"]:
                continue
            if tag_filter and not (tag_filter & doc["tags"]):
                continue
            if taxonomy_filter and not (taxonomy_filter & doc["taxonomy"]):
                continue
            if source_filter and doc["source_type"] not in source_filter:
                continue
            results.append(entry_id)
        return results
