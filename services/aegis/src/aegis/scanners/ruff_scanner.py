from __future__ import annotations

import json
import subprocess
from typing import List

from ..models import Finding, Severity
from .base import Scanner


class RuffScanner(Scanner):
    """Scanner that uses ruff for Python linting."""

    @property
    def name(self) -> str:
        return "ruff"

    def scan(self, repo_path: str) -> List[Finding]:
        """Run ruff check and return findings."""
        findings: List[Finding] = []

        try:
            result = subprocess.run(
                ["ruff", "check", repo_path, "--output-format=json"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.stdout:
                ruff_output = json.loads(result.stdout)

                for issue in ruff_output:
                    severity = self._map_severity(issue.get("code", ""))
                    findings.append(
                        Finding(
                            id=None,
                            rule_id=f"ruff-{issue.get('code', 'unknown')}",
                            message=issue.get("message", "Ruff violation"),
                            severity=severity,
                            path=issue.get("filename"),
                            line=issue.get("location", {}).get("row"),
                            extra={
                                "code": issue.get("code"),
                                "url": issue.get("url"),
                            },
                        )
                    )

        except subprocess.TimeoutExpired:
            findings.append(
                Finding(
                    id=None,
                    rule_id="ruff-timeout",
                    message="Ruff scanner timed out",
                    severity=Severity.MEDIUM,
                )
            )
        except FileNotFoundError:
            findings.append(
                Finding(
                    id=None,
                    rule_id="ruff-not-found",
                    message="Ruff binary not found in PATH",
                    severity=Severity.INFO,
                )
            )
        except Exception as e:
            findings.append(
                Finding(
                    id=None,
                    rule_id="ruff-error",
                    message=f"Ruff scanner failed: {str(e)}",
                    severity=Severity.MEDIUM,
                )
            )

        return findings

    def _map_severity(self, code: str) -> Severity:
        """Map ruff error code to Aegis severity."""
        if not code:
            return Severity.LOW

        prefix = code[0] if code else ""

        if prefix in ["F", "E"]:
            return Severity.MEDIUM
        elif prefix in ["W", "N"]:
            return Severity.LOW
        elif prefix in ["C", "R"]:
            return Severity.LOW
        elif prefix == "S":
            return Severity.HIGH
        else:
            return Severity.LOW
