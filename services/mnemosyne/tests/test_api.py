from importlib import reload

import pytest

from mnemosyne.presentation.api import main


def test_api_requires_key(monkeypatch):
    monkeypatch.setenv("MNEMO_API_KEY", "secret")
    reload(main)

    # health should remain public
    assert main.health()["status"] == "ok"

    with pytest.raises(Exception):
        main.require_api_key(None)

    # valid key should pass
    main.require_api_key("secret")
    assert main.search() == []
