from fastapi import APIRouter

router = APIRouter()

@router.post("/progress")
async def upsert_progress():
    # TODO: prompts/backend/04_reading_progress.md
    return {"status": "not_implemented"}

@router.get("/progress/{book_id}")
async def get_progress(book_id: str):
    # TODO
    return {"book_id": book_id}

@router.post("/sessions/start")
async def start_session():
    # TODO: prompts/backend/05_reading_sessions.md
    return {"status": "not_implemented"}

@router.post("/sessions/end")
async def end_session():
    # TODO
    return {"status": "not_implemented"}
