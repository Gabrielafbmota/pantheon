import os
from typing import Optional

from pymongo import MongoClient

from ..models import Scan
from ..repositories import ReportRepository


class MongoReportRepository(ReportRepository):
    def __init__(self, uri: Optional[str] = None, database: str = "aegis"):
        self.uri = uri or os.getenv("MONGO_URI")
        if not self.uri:
            raise EnvironmentError("MONGO_URI is required for MongoReportRepository")
        self.client = MongoClient(self.uri)
        self.db = self.client[database]

    def save(self, scan: Scan) -> str:
        doc = scan.dict()
        result = self.db.reports.insert_one(doc)
        return str(result.inserted_id)

    def get(self, report_id: str) -> Scan:
        doc = self.db.reports.find_one({"_id": report_id})
        if not doc:
            raise KeyError("report not found")
        return Scan(**doc)
