from __future__ import annotations

from typing import List

from .models import Scan, Baseline, Waiver


class ReportRepository:
    """Persistence interface for scans/reports."""

    def save(self, scan: Scan) -> str:
        raise NotImplementedError()

    def get(self, report_id: str) -> Scan:
        raise NotImplementedError()


class BaselineRepository:
    def save(self, baseline: Baseline) -> str:
        raise NotImplementedError()

    def get_for_repo(self, repo: str) -> Baseline:
        raise NotImplementedError()


class WaiverRepository:
    def save(self, waiver: Waiver) -> str:
        raise NotImplementedError()

    def list_active(self) -> List[Waiver]:
        raise NotImplementedError()
