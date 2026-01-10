from fastapi import Depends

from codexathenae.application.use_cases import ListBooks
from codexathenae.infrastructure.mongo import get_database
from codexathenae.infrastructure.repositories import MongoBooksRepository, ensure_books_indexes


async def get_books_collection():
    db = get_database()
    collection = db["books"]
    await ensure_books_indexes(collection)
    return collection


async def get_books_repository(collection=Depends(get_books_collection)) -> MongoBooksRepository:
    return MongoBooksRepository(collection)


async def get_list_books_use_case(repo=Depends(get_books_repository)) -> ListBooks:
    return ListBooks(repo)

