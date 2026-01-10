from typing import Protocol, Tuple, List

from codexathenae.application.dtos import ListBooksRequest, ListBooksResponse
from codexathenae.domain.entities import Book


class BooksRepository(Protocol):
    async def list_books(self, query: ListBooksRequest) -> Tuple[List[Book], int]:
        """Return a tuple (items, total) honoring pagination and filters."""
        ...


class ListBooks:
    def __init__(self, repository: BooksRepository):
        self.repository = repository

    async def execute(self, query: ListBooksRequest) -> ListBooksResponse:
        books, total = await self.repository.list_books(query)
        return ListBooksResponse.from_results(books, page=query.page, limit=query.limit, total=total)

