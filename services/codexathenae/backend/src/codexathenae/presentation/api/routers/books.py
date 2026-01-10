from typing import Optional

from fastapi import APIRouter, Depends, Header, Query

from codexathenae.application.dtos import ListBooksRequest, ListBooksResponse
from codexathenae.application.use_cases import ListBooks
from codexathenae.presentation.api.dependencies import get_list_books_use_case

router = APIRouter()


class ListBooksQuery(ListBooksRequest):
    page: int = Query(default=1, ge=1, description="Página começando em 1")
    limit: int = Query(default=20, ge=1, le=100, description="Quantidade por página (máx 100)")
    q: Optional[str] = Query(default=None, max_length=200, description="Busca por título/autor/descrição")
    author: Optional[str] = Query(default=None, max_length=120, description="Filtro por autor (case-insensitive)")
    genre: Optional[str] = Query(default=None, max_length=120, description="Filtro por gênero (case-insensitive)")
    has_isbn: Optional[bool] = Query(default=None, description="Filtra por presença de ISBN")


@router.get("", response_model=ListBooksResponse)
async def list_books(
    query: ListBooksQuery = Depends(),
    use_case: ListBooks = Depends(get_list_books_use_case),
    request_id: Optional[str] = Header(default=None, alias="X-Request-Id"),
):
    # request_id mantido para rastreabilidade (log/observabilidade)
    return await use_case.execute(query)

@router.post("")
async def create_book():
    # TODO: implementar (ver prompts/backend/02_books_create_dedupe.md)
    return {"status": "not_implemented"}

@router.get("/{book_id}")
async def get_book(book_id: str):
    # TODO
    return {"id": book_id}

@router.put("/{book_id}")
async def update_book(book_id: str):
    # TODO
    return {"status": "not_implemented", "id": book_id}

@router.delete("/{book_id}")
async def delete_book(book_id: str):
    # TODO
    return {"status": "not_implemented", "id": book_id}
