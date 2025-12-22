from __future__ import annotations

import os
from typing import Protocol, Any

from mnemosyne.domain.contracts import RawDocumentStorage


class _S3ClientFactory(Protocol):
    def __call__(self) -> BaseClient: ...


class S3RawDocumentStorage(RawDocumentStorage):
    """
    Simple S3-backed raw document storage.

    Uses a pre-configured bucket (MNEMO_S3_BUCKET) and stores objects under run_id/external_id.
    Intended for small payloads; caller is responsible for size validation upstream.
    """

    def __init__(self, bucket: str | None = None, client: Any | None = None, factory: _S3ClientFactory | None = None) -> None:
        self.bucket = bucket or os.getenv("MNEMO_S3_BUCKET", "")
        if not self.bucket:
            raise ValueError("MNEMO_S3_BUCKET is required for S3RawDocumentStorage")
        self._client = client
        self._factory = factory

    @property
    def client(self):
        if self._client:
            return self._client
        if self._factory:
            self._client = self._factory()
        else:
            try:
                import boto3  # type: ignore
            except ImportError as exc:  # pragma: no cover - tested via unit tests
                raise RuntimeError("boto3 is required for S3RawDocumentStorage") from exc
            self._client = boto3.client("s3")
        return self._client

    def store(self, run_id: str, external_id: str, content: str) -> str:
        key = f"runs/{run_id}/{external_id}.txt"
        self.client.put_object(Bucket=self.bucket, Key=key, Body=content.encode("utf-8"))
        return f"s3://{self.bucket}/{key}"
