from fastapi import APIRouter

router = APIRouter()

@router.post("")
async def create_highlight():
    # TODO: prompts/backend/06_highlights.md
    return {"status": "not_implemented"}

@router.get("/{book_id}")
async def list_highlights(book_id: str):
    # TODO
    return {"items": [], "book_id": book_id}
