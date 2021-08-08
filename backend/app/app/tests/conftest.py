import json
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from redis import Redis

from app.core.config import settings
from app.main import app


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def rate_cdr_obj():
    return json.dumps(
        {
            "rate": {"energy": 0.3, "time": 2, "transaction": 1},
            "cdr": {
                "timestamp_start": "2021-04-05T10:04:00Z",
                "timestamp_stop": "2021-04-05T11:27:00Z",
                "meter_start": 1204307,
                "meter_stop": 1215230,
            },
        }
    )


redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


@pytest.fixture
def clear_cache():
    def _clear_cache():
        redis.flushdb()

    _clear_cache()
    return _clear_cache
