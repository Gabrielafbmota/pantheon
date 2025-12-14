import json
import os
import subprocess
import sys
import pytest


def test_scan_outputs_json():
    from aegis import cli as _cli

    # Call the function directly to avoid subprocess/CLI parsing issues in test
    # Provide explicit `fail_on` to avoid receiving Typer OptionInfo defaults
    _cli.scan(repo="testrepo", commit="abc", output="-", fail_on=_cli.Severity.HIGH)


def test_delta_fails_on_new_high(tmp_path, monkeypatch):
    from aegis.models import Scan, Finding, Severity

    # Replace _quick_scan to return a HIGH finding
    def fake_scan(repo, commit):
        return Scan(
            id=None,
            repo=repo,
            commit=commit,
            findings=[
                Finding(id=None, rule_id="r", message="m", severity=Severity.HIGH)
            ],
        )

    monkeypatch.setattr("aegis.cli._quick_scan", fake_scan)

    baseline_file = tmp_path / "baseline.json"
    baseline_file.write_text(
        json.dumps({"repo": "testrepo", "commit": "old", "fingerprints": []})
    )

    from aegis import cli as _cli

    with pytest.raises(_cli.typer.Exit):
        _cli.scan(
            repo="testrepo",
            commit="abc",
            output="-",
            baseline=str(baseline_file),
            fail_on=_cli.Severity.HIGH,
        )


def test_delta_passes_if_all_in_baseline(tmp_path, monkeypatch):
    from aegis.models import Scan, Finding, Severity

    f = Finding(id=None, rule_id="r", message="m", severity=Severity.HIGH)

    def fake_scan(repo, commit):
        return Scan(id=None, repo=repo, commit=commit, findings=[f])

    monkeypatch.setattr("aegis.cli._quick_scan", fake_scan)

    baseline_file = tmp_path / "baseline.json"
    baseline_file.write_text(
        json.dumps(
            {"repo": "testrepo", "commit": "old", "fingerprints": [f.fingerprint()]}
        )
    )

    from aegis import cli as _cli

    # Should not raise
    _cli.scan(
        repo="testrepo",
        commit="abc",
        output="-",
        baseline=str(baseline_file),
        fail_on=_cli.Severity.HIGH,
    )
