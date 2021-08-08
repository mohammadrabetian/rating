import json
from numbers import Number

from fastapi.testclient import TestClient

from app.core.config import settings

headers = {"API-Key": settings.API_KEY_SECRET}


def test_api_schema_validation_greater_than_zero(
    client: TestClient, rate_cdr_obj: dict
) -> None:
    rate_cdr_obj = json.loads(rate_cdr_obj)
    rate_cdr_obj["rate"]["energy"] = 0
    rate_cdr_obj["rate"]["time"] = 0
    rate_cdr_obj["rate"]["transaction"] = 0
    rate_cdr_obj = json.dumps(rate_cdr_obj)
    expected_output = {
        "detail": [
            {
                "loc": ["body", "rate", "energy"],
                "msg": "ensure this value is greater than 0",
                "type": "value_error.number.not_gt",
                "ctx": {"limit_value": 0},
            },
            {
                "loc": ["body", "rate", "time"],
                "msg": "ensure this value is greater than 0",
                "type": "value_error.number.not_gt",
                "ctx": {"limit_value": 0},
            },
            {
                "loc": ["body", "rate", "transaction"],
                "msg": "ensure this value is greater than 0",
                "type": "value_error.number.not_gt",
                "ctx": {"limit_value": 0},
            },
        ]
    }
    r = client.post(f"{settings.API_V1_STR}/rate/", data=rate_cdr_obj, headers=headers)
    assert r.status_code == 422
    assert r.json() == expected_output


def test_api_correct_result(client: TestClient, rate_cdr_obj: dict) -> None:
    expected_output = {
        "overall": 7.04,
        "components": {"energy": 3.277, "time": 2.767, "transaction": 1},
    }
    r = client.post(f"{settings.API_V1_STR}/rate/", data=rate_cdr_obj, headers=headers)
    assert r.status_code == 200
    assert r.json() == expected_output


def test_default_currency(client: TestClient, clear_cache) -> None:
    expected_output = {
        "overall": 10,
        "components": {"energy": 4, "time": 3, "transaction": 3},
        "currency": "EUR",
    }

    r = client.get(
        f"{settings.API_V1_STR}/rate/converted-rate/",
        headers=headers,
        params=[
            ("overall", 10),
            ("energy", 4),
            ("time", 3),
            ("transaction", 3),
            ("currency", "EUR"),
        ],
    )
    assert r.status_code == 200
    assert r.json() == expected_output


def test_currency_conversion(client: TestClient, clear_cache) -> None:

    r = client.get(
        f"{settings.API_V1_STR}/rate/converted-rate/",
        headers=headers,
        params=[
            ("overall", 10),
            ("energy", 4),
            ("time", 3),
            ("transaction", 3),
            ("currency", "USD"),
        ],
    )
    assert r.status_code == 200
    result = r.json()
    assert isinstance(result.get("overall"), Number)
