import pytest

from aegis.adapters.mongo_repository import MongoReportRepository


def test_mongo_repo_requires_uri_env_var():
    # Ensure that without MONGO_URI the repository raises
    import os

    old = os.environ.pop("MONGO_URI", None)
    try:
        with pytest.raises(EnvironmentError):
            MongoReportRepository()
    finally:
        if old is not None:
            os.environ["MONGO_URI"] = old
