from __future__ import annotations

from typing import Dict, List, Set


class SimpleTextIndex:
    def __init__(self) -> None:
        self._index: Dict[str, Set[str]] = {}

    def index(self, entry_id: str, text: str) -> None:
        for token in text.lower().split():
            if len(token) < 3:
                continue
            self._index.setdefault(token, set()).add(entry_id)

    def search(self, query: str) -> List[str]:
        tokens = query.lower().split()
        if not tokens:
            return []
        matching_sets = [self._index.get(token, set()) for token in tokens]
        if not matching_sets:
            return []
        result = set.intersection(*matching_sets) if len(matching_sets) > 1 else matching_sets[0]
        return list(result)
