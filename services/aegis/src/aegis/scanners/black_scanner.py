from __future__ import annotations

import subprocess
from typing import List

from ..models import Finding, Severity
from .base import Scanner


class BlackScanner(Scanner):
    """Scanner that checks Python code formatting with black."""

    @property
    def name(self) -> str:
        return "black"

    def scan(self, repo_path: str) -> List[Finding]:
        """Run black --check and return findings."""
        findings: List[Finding] = []

        try:
            result = subprocess.run(
                ["black", "--check", repo_path],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0 and result.stderr:
                lines = result.stderr.strip().split("\n")
                for line in lines:
                    if "would reformat" in line.lower():
                        path = line.split()[2] if len(line.split()) > 2 else None
                        findings.append(
                            Finding(
                                id=None,
                                rule_id="black-format",
                                message=f"File would be reformatted: {line}",
                                severity=Severity.LOW,
                                path=path,
                            )
                        )

        except subprocess.TimeoutExpired:
            findings.append(
                Finding(
                    id=None,
                    rule_id="black-timeout",
                    message="Black scanner timed out",
                    severity=Severity.MEDIUM,
                )
            )
        except FileNotFoundError:
            findings.append(
                Finding(
                    id=None,
                    rule_id="black-not-found",
                    message="Black binary not found in PATH",
                    severity=Severity.INFO,
                )
            )
        except Exception as e:
            findings.append(
                Finding(
                    id=None,
                    rule_id="black-error",
                    message=f"Black scanner failed: {str(e)}",
                    severity=Severity.MEDIUM,
                )
            )

        return findings
