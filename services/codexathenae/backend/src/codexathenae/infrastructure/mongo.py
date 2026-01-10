from functools import lru_cache
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from codexathenae.config import Settings, get_settings


@lru_cache
def get_mongo_client(settings: Settings | None = None) -> AsyncIOMotorClient:
    cfg = settings or get_settings()
    return AsyncIOMotorClient(cfg.mongo_db_uri)


def get_database(settings: Settings | None = None) -> AsyncIOMotorDatabase:
    cfg = settings or get_settings()
    client = get_mongo_client(cfg)
    return client[cfg.mongo_db_name]

