import json

from fastapi.testclient import TestClient

from app.core.config import settings


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
    headers = {"API-Key": settings.API_KEY_SECRET}
    r = client.post(f"{settings.API_V1_STR}/rate/", data=rate_cdr_obj, headers=headers)
    assert r.status_code == 422
    assert r.json() == expected_output


def test_api_correct_result(client: TestClient, rate_cdr_obj: dict) -> None:
    expected_output = {
        "overall": 7.04,
        "components": {"energy": 3.277, "time": 2.767, "transaction": 1},
    }
    headers = {"API-Key": settings.API_KEY_SECRET}
    r = client.post(f"{settings.API_V1_STR}/rate/", data=rate_cdr_obj, headers=headers)
    assert r.status_code == 200
    assert r.json() == expected_output
