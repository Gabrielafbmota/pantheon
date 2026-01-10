from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

# Load .env early so FastAPI dependencies and scripts see values without extra calls
load_dotenv()


class Settings(BaseModel):
    model_config = ConfigDict(extra="ignore", env_prefix="", populate_by_name=True)

    app_name: str = Field(default="CodexAthenae API", alias="APP_NAME")
    app_env: str = Field(default="dev", alias="APP_ENV")

    mongo_db_uri: str = Field(default="mongodb://localhost:27017", alias="MONGO_DB_URI")
    mongo_db_name: str = Field(default="codexathenae", alias="MONGO_DB_NAME")

    cors_origins: Optional[str] = Field(default=None, alias="CORS_ORIGINS")


@lru_cache
def get_settings() -> Settings:
    return Settings()

