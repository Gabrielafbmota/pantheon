"""Importa livros de `codexathenae.books.json` para MongoDB de forma idempotente.

- Preserva dados existentes
- Upsert por ISBN; sem ISBN, por fingerprint (title+authors normalizados)
- Não apaga nada
- Logs com loguru

Uso:
    python -m scripts.import_books --json ../data/codexathenae.books.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError
from uuid import uuid4


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def norm(s: str) -> str:
    s = (s or "").strip().lower()
    # remove pontuação simples
    out = []
    for ch in s:
        if ch.isalnum() or ch.isspace():
            out.append(ch)
    return " ".join("".join(out).split())


def fingerprint(title: str, authors: List[str]) -> str:
    base = norm(title) + "|" + "|".join(norm(a) for a in (authors or []))
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def ensure_uuid(v: Optional[str]) -> str:
    return v if v else str(uuid4())


def map_book(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normaliza um item do JSON para o schema expandido sem quebrar o legado."""
    now = utcnow()

    title = raw.get("title") or raw.get("Title") or ""
    authors = raw.get("authors") or raw.get("Authors") or []
    if isinstance(authors, str):
        authors = [a.strip() for a in authors.split(",") if a.strip()]

    isbn = raw.get("isbn") or raw.get("ISBN") or None
    genre = raw.get("genre") or raw.get("Genre") or None

    doc = {
        # legado
        "id": ensure_uuid(raw.get("id") or raw.get("Id")),
        "title": title,
        "authors": authors,
        "publishedDate": raw.get("publishedDate") or raw.get("published_date") or raw.get("PublishedDate"),
        "publishDate": raw.get("publishDate") or raw.get("publish_date") or raw.get("PublishDate"),
        "description": raw.get("description") or raw.get("Description"),
        "imageLinks": raw.get("imageLinks") or raw.get("image_links") or raw.get("ImageLinks"),
        "isbn": isbn,
        "genre": genre,
        # expandido
        "publisher": raw.get("publisher") or raw.get("Publisher"),
        "tags": raw.get("tags") or [],
        "rating": raw.get("rating"),
        "metadata": raw.get("metadata") or {
            "source": "import_json",
            "source_id": raw.get("source_id"),
            "fetched_at": now,
        },
        "created_at": raw.get("created_at") or now,
        "updated_at": now,
        "_fingerprint": fingerprint(title, authors),
        "_title_norm": norm(title),
    }
    # garantir lista
    if not isinstance(doc["tags"], list):
        doc["tags"] = []
    return doc


async def ensure_indexes(col):
    # índices para busca e dedupe
    await col.create_index([("isbn", ASCENDING)], name="idx_isbn", sparse=True)
    await col.create_index([("_fingerprint", ASCENDING)], name="idx_fingerprint")
    await col.create_index([("_title_norm", ASCENDING)], name="idx_title_norm")
    await col.create_index([("authors", ASCENDING)], name="idx_authors")
    # índice único opcional para isbn quando existir
    # (sparse + unique funciona para evitar duplicados com isbn)
    await col.create_index([("isbn", ASCENDING)], name="uq_isbn", unique=True, sparse=True)


async def upsert_book(col, doc: Dict[str, Any]) -> Tuple[str, str]:
    """Retorna (action, id): action in {inserted, updated, skipped}"""
    isbn = doc.get("isbn")
    fp = doc.get("_fingerprint")

    existing = None
    if isbn:
        existing = await col.find_one({"isbn": isbn})
    if not existing and fp:
        existing = await col.find_one({"_fingerprint": fp})

    if existing:
        # update leve: preservar campos existentes e preencher ausentes
        update_fields = {}
        for k, v in doc.items():
            if k in ("created_at",):
                continue
            if v is None or v == "" or v == []:
                continue
            # só sobrescreve se existente for vazio
            if existing.get(k) in (None, "", []):
                update_fields[k] = v
        update_fields["updated_at"] = utcnow()
        if update_fields:
            await col.update_one({"_id": existing["_id"]}, {"$set": update_fields})
            return "updated", existing.get("id", doc["id"])
        return "skipped", existing.get("id", doc["id"])

    try:
        await col.insert_one(doc)
        return "inserted", doc["id"]
    except DuplicateKeyError:
        # corrida em índice único isbn
        existing = await col.find_one({"isbn": isbn}) if isbn else await col.find_one({"_fingerprint": fp})
        return "skipped", (existing or {}).get("id", doc["id"])


async def main_async(json_path: str, mongo_uri: str, db_name: str):
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    col = db["books"]

    await ensure_indexes(col)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "books" in data:
        books = data["books"]
    else:
        books = data

    total = 0
    inserted = 0
    updated = 0
    skipped = 0
    errors = 0

    for raw in books:
        total += 1
        try:
            doc = map_book(raw)
            action, bid = await upsert_book(col, doc)
            if action == "inserted":
                inserted += 1
            elif action == "updated":
                updated += 1
            else:
                skipped += 1
            logger.info(f"[{action}] id={bid} isbn={doc.get('isbn')} title={doc.get('title')}")
        except Exception as e:
            errors += 1
            logger.exception(f"[error] item={total} err={e}")

    logger.info(
        f"Import finalizado: total={total} inserted={inserted} updated={updated} skipped={skipped} errors={errors}"
    )
    client.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--json", dest="json_path", required=True, help="Caminho para codexathenae.books.json")
    p.add_argument("--mongo-uri", dest="mongo_uri", default=os.getenv("MONGO_DB_URI", "mongodb://localhost:27017"))
    p.add_argument("--db", dest="db_name", default=os.getenv("MONGO_DB_NAME", "codexathenae"))
    args = p.parse_args()

    import asyncio
    asyncio.run(main_async(args.json_path, args.mongo_uri, args.db_name))


if __name__ == "__main__":
    main()
