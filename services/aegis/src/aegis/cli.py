from __future__ import annotations

import json
import sys
from typing import List, Optional

import typer

from .models import Finding, Scan, Severity
from .adapters.mongo_repository import MongoReportRepository

app = typer.Typer(help="Aegis — quality and security gate CLI")


def _quick_scan(repo: str, commit: str) -> Scan:
    """A very small MVP scanner that returns deterministic findings for demo/tests."""
    findings: List[Finding] = []

    # Dummy lint finding
    findings.append(
        Finding(
            id=None,
            rule_id="lint-unused-import",
            message="Unused import detected in module",
            severity=Severity.LOW,
            path="src/example.py",
            line=10,
        )
    )

    # Dummy secret detection if string SECRET found in files (MVP: env-driven)
    # We keep it deterministic and off by default.

    return Scan(id=None, repo=repo, commit=commit, findings=findings)


@app.command()
def scan(
    repo: str = typer.Option(".", help="Repository path or name"),
    commit: str = typer.Option("HEAD", help="Commit/ref being scanned"),
    output: str = typer.Option("-", help="Output file (- for stdout)"),
    fail_on: Severity = typer.Option(
        Severity.HIGH, help="Fail if any finding >= this severity"
    ),
    baseline: Optional[str] = typer.Option(
        None, help="Path to baseline JSON file containing fingerprints"
    ),
):
    """Run a scan and emit a JSON report."""
    scan_result = _quick_scan(repo=repo, commit=commit)

    # Serialize
    payload = scan_result.dict()
    out_text = json.dumps(payload, default=str, sort_keys=True, indent=2)

    if output == "-":
        typer.echo(out_text)
    else:
        with open(output, "w", encoding="utf-8") as fh:
            fh.write(out_text)

    # Determine exit code by severity and baseline delta
    severity_order = [s for s in Severity]

    # convert fail_on to index
    idx = severity_order.index(fail_on)

    # If any CRITICAL findings exist, fail immediately (requires explicit approval)
    for f in scan_result.findings:
        if f.severity == Severity.CRITICAL:
            raise typer.Exit(code=1)

    # Normalize baseline when called programmatically (Typer OptionInfo defaults)
    baseline_path = None
    try:
        from typer.models import OptionInfo

        if isinstance(baseline, OptionInfo):
            baseline_path = None
        else:
            baseline_path = baseline
    except Exception:
        baseline_path = baseline

    # Load baseline if provided and compute delta
    if baseline_path:
        try:
            with open(baseline_path, "r", encoding="utf-8") as fh:
                import json as _json

                b = _json.load(fh)
                baseline_fps = set(b.get("fingerprints", []))
        except Exception:
            typer.echo("unable to read baseline file", err=True)
            raise typer.Exit(code=2)

        new_findings = []
        for f in scan_result.findings:
            if f.fingerprint() not in baseline_fps:
                new_findings.append(f)

        for f in new_findings:
            if severity_order.index(f.severity) >= idx:
                raise typer.Exit(code=1)

    else:
        for f in scan_result.findings:
            if severity_order.index(f.severity) >= idx:
                # non-zero exit
                raise typer.Exit(code=1)


@app.command()
def persist(
    input_file: str = typer.Option("-", help="JSON report file (- for stdin)"),
    mongo_uri: Optional[str] = typer.Option(
        None, help="MongoDB URI (overrides MONGO_URI env var)"
    ),
):
    """Persist a JSON scan report to MongoDB (MVP)."""
    if input_file == "-":
        text = sys.stdin.read()
    else:
        with open(input_file, "r", encoding="utf-8") as fh:
            text = fh.read()

    data = json.loads(text)
    scan = Scan(**data)
    repo = MongoReportRepository(uri=mongo_uri)
    inserted = repo.save(scan)
    typer.echo(inserted)


if __name__ == "__main__":
    app()


def main() -> None:
    """Entrypoint for console_scripts / Poetry."""
    app()
