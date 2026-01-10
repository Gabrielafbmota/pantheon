from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from codexathenae.presentation.api.routers import books, reading, highlights, health
from codexathenae.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0")

    cors_origins = ["*"]
    if settings.cors_origins:
        cors_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, tags=["health"])
    app.include_router(books.router, prefix="/books", tags=["books"])
    app.include_router(reading.router, prefix="/reading", tags=["reading"])
    app.include_router(highlights.router, prefix="/highlights", tags=["highlights"])

    return app


app = create_app()
