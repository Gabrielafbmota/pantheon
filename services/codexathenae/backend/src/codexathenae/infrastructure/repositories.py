import re
from typing import Any, Dict, List, Tuple

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ASCENDING, DESCENDING, TEXT

from codexathenae.application.dtos import ListBooksRequest
from codexathenae.domain.entities import Book


async def ensure_books_indexes(collection: AsyncIOMotorCollection) -> None:
    """Create indexes for the books collection (idempotent)."""
    await collection.create_index([("isbn", ASCENDING)], name="idx_isbn", sparse=True)
    await collection.create_index([("_fingerprint", ASCENDING)], name="idx_fingerprint")
    await collection.create_index([("_title_norm", ASCENDING)], name="idx_title_norm")
    await collection.create_index([("authors", ASCENDING)], name="idx_authors")
    await collection.create_index([("genre", ASCENDING)], name="idx_genre")
    await collection.create_index([("created_at", DESCENDING)], name="idx_created_at")
    await collection.create_index([("title", TEXT), ("description", TEXT), ("authors", TEXT)], name="idx_books_text")
    # unique isbn when available (sparse avoids missing isbn)
    await collection.create_index([("isbn", ASCENDING)], name="uq_isbn", unique=True, sparse=True)


class MongoBooksRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    def _build_filters(self, query: ListBooksRequest) -> Dict[str, Any]:
        clauses: List[Dict[str, Any]] = []

        if query.q:
            regex = {"$regex": re.escape(query.q), "$options": "i"}
            clauses.append(
                {"$or": [{"title": regex}, {"authors": regex}, {"description": regex}, {"genre": regex}]}
            )

        if query.author:
            clauses.append({"authors": {"$regex": re.escape(query.author), "$options": "i"}})

        if query.genre:
            clauses.append({"genre": {"$regex": f"^{re.escape(query.genre)}$", "$options": "i"}})

        if query.has_isbn is True:
            clauses.append({"isbn": {"$exists": True, "$nin": [None, ""]}})
        elif query.has_isbn is False:
            clauses.append({"$or": [{"isbn": {"$exists": False}}, {"isbn": None}, {"isbn": ""}]})

        if not clauses:
            return {}
        if len(clauses) == 1:
            return clauses[0]
        return {"$and": clauses}

    async def list_books(self, query: ListBooksRequest) -> Tuple[List[Book], int]:
        filters = self._build_filters(query)
        skip = (query.page - 1) * query.limit

        cursor = (
            self.collection.find(filters)
            .sort([("title", ASCENDING), ("_id", ASCENDING)])
            .skip(skip)
            .limit(query.limit)
        )

        items = await cursor.to_list(length=query.limit)
        total = await self.collection.count_documents(filters)

        books = [Book.model_validate(item) for item in items]
        return books, total

