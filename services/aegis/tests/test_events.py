from aegis.adapters.events import MnemosynePublisher, EyeOfHorusPublisher


def test_publish_mnemosyne():
    p = MnemosynePublisher()
    r = p.publish({"repo": "test"})
    assert r.startswith("mnemosyne:")


def test_emit_eyeofhorus():
    p = EyeOfHorusPublisher()
    r = p.emit({"severity": "CRITICAL"})
    assert r.startswith("eyeofhorus:")
