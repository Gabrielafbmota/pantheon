import re
import sys
from pathlib import Path
from typing import Any, Dict, List

import pytest

# Ensure `src` is importable when running pytest from the backend directory
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


class AsyncCursorMock:
    def __init__(self, docs: List[Dict[str, Any]]):
        self.docs = list(docs)

    def sort(self, key_or_list, direction=None):
        if isinstance(key_or_list, list):
            keys = key_or_list
        else:
            keys = [(key_or_list, direction or 1)]

        for key, dir_value in reversed(keys):
            reverse = dir_value == -1
            self.docs.sort(key=lambda d: d.get(key), reverse=reverse)
        return self

    def skip(self, n: int):
        self.docs = self.docs[n:]
        return self

    def limit(self, n: int):
        self.docs = self.docs[:n]
        return self

    async def to_list(self, length: int):
        return list(self.docs[:length])


class AsyncCollectionMock:
    """Lightweight async-friendly collection used for repository tests."""

    def __init__(self):
        self._docs: List[Dict[str, Any]] = []
        self._indexes: List[Any] = []

    def insert_many(self, docs: List[Dict[str, Any]]):
        self._docs.extend(docs)
        return {"inserted": len(docs)}

    def _matches_condition(self, doc: Dict[str, Any], condition: Dict[str, Any]) -> bool:
        if not condition:
            return True

        for key, value in condition.items():
            if key == "$and":
                return all(self._matches_condition(doc, sub) for sub in value)
            if key == "$or":
                return any(self._matches_condition(doc, sub) for sub in value)

            if isinstance(value, dict):
                if "$regex" in value:
                    pattern = re.compile(value["$regex"], re.IGNORECASE if "i" in value.get("$options", "") else 0)
                    field_value = doc.get(key, "")
                    if isinstance(field_value, list):
                        field_value = " ".join(field_value)
                    if field_value is None or not pattern.search(str(field_value)):
                        return False
                if "$exists" in value:
                    exists = key in doc and doc.get(key) is not None
                    if value["$exists"] != exists:
                        return False
                if "$nin" in value:
                    if doc.get(key) in value["$nin"]:
                        return False
                if "$in" in value:
                    if doc.get(key) not in value["$in"]:
                        return False
                # if we matched operators, skip equality check
                if any(op in value for op in ("$regex", "$exists", "$nin", "$in")):
                    continue
            if doc.get(key) != value:
                return False
        return True

    def find(self, filter: Dict[str, Any] | None = None, *args, **kwargs):
        filter = filter or {}
        filtered = [doc for doc in self._docs if self._matches_condition(doc, filter)]
        return AsyncCursorMock(filtered)

    async def count_documents(self, filter: Dict[str, Any] | None = None, **kwargs):
        filter = filter or {}
        return len([doc for doc in self._docs if self._matches_condition(doc, filter)])

    async def create_index(self, *args, **kwargs):
        self._indexes.append((args, kwargs))
        return "idx"


@pytest.fixture
def async_books_collection():
    return AsyncCollectionMock()
