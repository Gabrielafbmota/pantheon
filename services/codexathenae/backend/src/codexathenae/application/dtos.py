from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from codexathenae.domain.entities import Book


class ListBooksRequest(BaseModel):
    """Validated query parameters for listing books."""

    model_config = ConfigDict(populate_by_name=True)

    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    q: Optional[str] = Field(default=None, max_length=200)
    author: Optional[str] = Field(default=None, max_length=120)
    genre: Optional[str] = Field(default=None, max_length=120)
    has_isbn: Optional[bool] = Field(default=None, alias="has_isbn")


class BookResponse(BaseModel):
    """Response-friendly view of a Book."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    id: str
    title: str
    authors: List[str]
    isbn: Optional[str] = None
    genre: Optional[str] = None
    description: Optional[str] = None
    imageLinks: Optional[str] = None
    publishedDate: Optional[str] = None
    publishDate: Optional[str] = None


class ListBooksResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: List[BookResponse]
    page: int
    limit: int
    total: int

    @classmethod
    def from_results(cls, books: List[Book], page: int, limit: int, total: int) -> "ListBooksResponse":
        return cls(
            items=[BookResponse.model_validate(book) for book in books],
            page=page,
            limit=limit,
            total=total,
        )

