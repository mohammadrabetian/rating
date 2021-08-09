import json
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from redis import Redis

from app.core.config import settings
from app.main import app


@pytest.fixture()
def client() -> Generator:
    with TestClient(app) as c:
        yield c


# Seperate redis database for the tests
@pytest.fixture
async def redis_test_database():
    from app.main import shutdown_event, startup_event

    await startup_event(db=1)
    yield
    await shutdown_event()


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


@pytest.fixture
def redis_connection():
    return Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


@pytest.fixture
def clear_cache(redis_connection):
    def _clear_cache():
        redis_connection.flushdb()

    _clear_cache()
    return _clear_cache


@pytest.fixture
def raw_conversion_result():
    return {
        "motd": {
            "msg": "If you or your company use this project or like what we doing, please consider backing us so we can continue maintaining and evolving this project.",
            "url": "https://exchangerate.host/#/donate",
        },
        "success": True,
        "query": {"from": "EUR", "to": "USD", "amount": 10},
        "info": {"rate": 1.176132},
        "historical": False,
        "date": "2021-08-08",
        "result": 11.761324,
    }
