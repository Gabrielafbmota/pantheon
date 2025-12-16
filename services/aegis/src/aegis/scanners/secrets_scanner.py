from __future__ import annotations

import json
import subprocess
from typing import List

from ..models import Finding, Severity
from .base import Scanner


class SecretsScanner(Scanner):
    """Scanner that detects secrets using detect-secrets."""

    @property
    def name(self) -> str:
        return "detect-secrets"

    def scan(self, repo_path: str) -> List[Finding]:
        """Run detect-secrets and return findings."""
        findings: List[Finding] = []

        try:
            result = subprocess.run(
                ["detect-secrets", "scan", repo_path, "--all-files"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.stdout:
                try:
                    secrets_output = json.loads(result.stdout)
                    results = secrets_output.get("results", {})

                    for filepath, secrets in results.items():
                        for secret in secrets:
                            findings.append(
                                Finding(
                                    id=None,
                                    rule_id=f"secret-{secret.get('type', 'unknown')}",
                                    message=f"Potential secret detected: {secret.get('type', 'unknown')}",
                                    severity=Severity.CRITICAL,
                                    path=filepath,
                                    line=secret.get("line_number"),
                                    extra={
                                        "type": secret.get("type"),
                                        "hashed_secret": secret.get("hashed_secret"),
                                    },
                                )
                            )
                except json.JSONDecodeError:
                    pass

        except subprocess.TimeoutExpired:
            findings.append(
                Finding(
                    id=None,
                    rule_id="secrets-timeout",
                    message="Secrets scanner timed out",
                    severity=Severity.MEDIUM,
                )
            )
        except FileNotFoundError:
            findings.append(
                Finding(
                    id=None,
                    rule_id="secrets-not-found",
                    message="detect-secrets binary not found in PATH",
                    severity=Severity.INFO,
                )
            )
        except Exception as e:
            findings.append(
                Finding(
                    id=None,
                    rule_id="secrets-error",
                    message=f"Secrets scanner failed: {str(e)}",
                    severity=Severity.MEDIUM,
                )
            )

        return findings
