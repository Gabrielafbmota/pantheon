from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any


class Book(BaseModel):
    """Core Book entity used across layers."""

    model_config = ConfigDict(extra="allow", populate_by_name=True, from_attributes=True)

    id: str
    title: str
    authors: List[str] = []
    isbn: Optional[str] = None
    genre: Optional[str] = None
    description: Optional[str] = None
    imageLinks: Optional[str] = None
    publishedDate: Optional[str] = None
    publishDate: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[Any] = None
    updated_at: Optional[Any] = None

