from __future__ import annotations

from enum import Enum
from hashlib import sha256
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Rule(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    severity: Severity = Severity.LOW
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Policy(BaseModel):
    id: str
    name: str
    version: str
    rules: List[Rule] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Finding(BaseModel):
    id: Optional[str]
    rule_id: str
    message: str
    severity: Severity
    path: Optional[str] = None
    line: Optional[int] = None
    extra: Dict[str, Any] = Field(default_factory=dict)

    def fingerprint(self) -> str:
        """Deterministic fingerprint for the finding"""
        # sort keys to keep deterministic
        payload = {
            "rule_id": self.rule_id,
            "message": self.message,
            "severity": self.severity.value,
            "path": self.path or "",
            "line": self.line or 0,
        }
        text = repr(sorted(payload.items()))
        return sha256(text.encode("utf-8")).hexdigest()


class Scan(BaseModel):
    id: Optional[str]
    repo: str
    commit: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    findings: List[Finding] = Field(default_factory=list)

    def summary(self) -> Dict[str, int]:
        counts: Dict[str, int] = {s.value: 0 for s in Severity}
        for f in self.findings:
            counts[f.severity.value] += 1
        return counts


class Baseline(BaseModel):
    repo: str
    commit: str
    fingerprints: List[str] = Field(default_factory=list)


class Waiver(BaseModel):
    id: Optional[str]
    finding_fingerprint: str
    justification: str
    owner: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
