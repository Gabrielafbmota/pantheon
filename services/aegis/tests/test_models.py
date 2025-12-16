from datetime import datetime, timedelta, timezone

from aegis.models import Finding, Severity


def test_fingerprint_deterministic():
    f1 = Finding(
        id=None,
        rule_id="r1",
        message="something",
        severity=Severity.LOW,
        path="a.py",
        line=1,
    )
    f2 = Finding(
        id=None,
        rule_id="r1",
        message="something",
        severity=Severity.LOW,
        path="a.py",
        line=1,
    )

    assert f1.fingerprint() == f2.fingerprint()


def test_waiver_dates():
    from aegis.models import Waiver

    w = Waiver(
        id=None,
        finding_fingerprint="abc",
        justification="ok",
        owner="alice",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    assert w.owner == "alice"
