from __future__ import annotations

from typing import Dict, List, Optional, Set

from pymongo.collection import Collection

from mnemosyne.domain.contracts import TextIndex
from mnemosyne.domain.entities.models import KnowledgeEntry


class MongoTextIndex(TextIndex):
    """
    Lightweight Mongo-backed index.

    Uses a dedicated collection with a projected document for filtering without requiring full-text indexes.
    """

    def __init__(self, collection: Collection) -> None:
        self.collection = collection
        self.collection.create_index("entry_id", unique=True)
        self.collection.create_index("source_type")

    def index(self, entry: KnowledgeEntry) -> None:
        version = entry.latest_version
        if not version:
            return
        doc: Dict[str, object] = {
            "entry_id": entry.id,
            "text": f"{version.normalized_content}\n{version.summary}".lower(),
            "tags": [t.key for t in version.tags],
            "taxonomy": version.taxonomy,
            "source_type": entry.source.type.value if hasattr(entry.source.type, "value") else entry.source.type,
        }
        self.collection.update_one({"entry_id": entry.id}, {"$set": doc}, upsert=True)

    def search(
        self,
        text: Optional[str] = None,
        tags: Optional[List[str]] = None,
        taxonomy: Optional[List[str]] = None,
        source_types: Optional[List[str]] = None,
    ) -> List[str]:
        query: Dict[str, object] = {}
        if source_types:
            query["source_type"] = {"$in": list(source_types)}
        docs = list(self.collection.find(query))
        results: List[str] = []
        text_q = (text or "").lower()
        tag_filter: Set[str] = set(tags or [])
        tax_filter: Set[str] = set(taxonomy or [])

        for doc in docs:
            if text_q and text_q not in (doc.get("text") or ""):
                continue
            doc_tags = set(doc.get("tags", []))
            doc_tax = set(doc.get("taxonomy", []))
            if tag_filter and not (tag_filter & doc_tags):
                continue
            if tax_filter and not (tax_filter & doc_tax):
                continue
            results.append(str(doc.get("entry_id")))
        return results
