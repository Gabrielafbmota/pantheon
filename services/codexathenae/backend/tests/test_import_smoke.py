import json
import pytest

def test_sample_json_schema():
    # smoke: garante que exemplo de item tenha campos esperados
    item = {
        "title": "Example",
        "authors": ["Someone"],
        "isbn": "9780000000000"
    }
    assert "title" in item
    assert isinstance(item["authors"], list)
