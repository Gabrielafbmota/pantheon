import asyncio

from httpx import ASGITransport, AsyncClient

from codexathenae.application.dtos import ListBooksRequest
from codexathenae.application.use_cases import ListBooks
from codexathenae.domain.entities import Book
from codexathenae.infrastructure.repositories import MongoBooksRepository
from codexathenae.presentation.api.dependencies import get_list_books_use_case
from codexathenae.presentation.api.main import create_app


class FakeBooksRepository:
    def __init__(self, items):
        self.items = [Book.model_validate(item) for item in items]

    async def list_books(self, query: ListBooksRequest):
        filtered = []
        for book in self.items:
            if query.author and not any(query.author.lower() in a.lower() for a in book.authors):
                continue
            if query.genre and (not book.genre or book.genre.lower() != query.genre.lower()):
                continue
            if query.has_isbn is True and not book.isbn:
                continue
            if query.has_isbn is False and book.isbn:
                continue
            if query.q:
                haystack = " ".join(
                    filter(
                        None,
                        [book.title, " ".join(book.authors), book.description or "", book.genre or ""],
                    )
                ).lower()
                if query.q.lower() not in haystack:
                    continue
            filtered.append(book)
        total = len(filtered)
        start = (query.page - 1) * query.limit
        end = start + query.limit
        return filtered[start:end], total


def test_use_case_paginates_and_filters():
    repo = FakeBooksRepository(
        [
            {"id": "1", "title": "The Hobbit", "authors": ["Tolkien"], "genre": "Fantasy", "isbn": "123"},
            {"id": "2", "title": "Silmarillion", "authors": ["Tolkien"], "genre": "Fantasy"},
            {"id": "3", "title": "Clean Code", "authors": ["Robert Martin"], "genre": "Tech", "isbn": "999"},
        ]
    )
    use_case = ListBooks(repo)

    query = ListBooksRequest(page=1, limit=2, author="tolkien", has_isbn=True)
    result = asyncio.run(use_case.execute(query))

    assert result.total == 1
    assert result.page == 1
    assert result.limit == 2
    assert len(result.items) == 1
    assert result.items[0].title == "The Hobbit"


def test_books_endpoint_returns_paginated_payload():
    app = create_app()
    repo = FakeBooksRepository(
        [
            {"id": "10", "title": "Example One", "authors": ["A"], "genre": "Fiction"},
            {"id": "11", "title": "Another Tale", "authors": ["B"], "genre": "Fiction"},
        ]
    )

    async def override_use_case():
        return ListBooks(repo)

    app.dependency_overrides[get_list_books_use_case] = override_use_case

    async def _call():
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            return await client.get("/books", params={"page": 1, "limit": 1, "q": "Example"})

    resp = asyncio.run(_call())
    assert resp.status_code == 200
    body = resp.json()
    assert body["page"] == 1
    assert body["limit"] == 1
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["title"] == "Example One"


def test_mongo_repository_filters_and_paginates(async_books_collection):
    async_books_collection.insert_many(
        [
            {"id": "1", "title": "Zero to One", "authors": ["Peter Thiel"], "genre": "Business", "isbn": "111"},
            {"id": "2", "title": "The Pragmatic Programmer", "authors": ["Andy Hunt"], "genre": "Tech", "isbn": "222"},
            {"id": "3", "title": "Domain-Driven Design", "authors": ["Eric Evans"], "genre": "Tech", "isbn": "333"},
            {"id": "4", "title": "Clean Architecture", "authors": ["Robert Martin"], "genre": "Tech"},
        ]
    )
    repo = MongoBooksRepository(async_books_collection)

    query = ListBooksRequest(page=1, limit=2, genre="Tech", has_isbn=True)
    books, total = asyncio.run(repo.list_books(query))

    assert total == 2
    assert len(books) == 2
    titles = [b.title for b in books]
    assert "The Pragmatic Programmer" in titles
    assert "Domain-Driven Design" not in titles  # missing isbn so filtered out
