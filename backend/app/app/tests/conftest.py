import json
from typing import Generator

import pytest
from fastapi.testclient import TestClient

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
