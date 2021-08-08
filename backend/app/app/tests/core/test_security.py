from fastapi.testclient import TestClient

from app.core.config import settings


def test_security_not_authorized(client: TestClient, rate_cdr_obj: dict) -> None:
    r = client.post(f"{settings.API_V1_STR}/rate/", data=rate_cdr_obj)
    assert r.status_code == 403
    assert r.json() == {"detail": "Not authenticated"}


def test_security_wrong_api_key(client: TestClient, rate_cdr_obj: dict) -> None:
    headers = {"Authorization-Header": "TOTALY-WRONG"}
    r = client.post(f"{settings.API_V1_STR}/rate/", data=rate_cdr_obj, headers=headers)
    assert r.status_code == 403
    assert r.json() == {"detail": "WRONG API KEY - not authorized"}


def test_security_correct_api_key(client: TestClient, rate_cdr_obj: dict) -> None:
    headers = {"Authorization-Header": settings.API_KEY_SECRET}
    r = client.post(f"{settings.API_V1_STR}/rate/", data=rate_cdr_obj, headers=headers)
    assert r.status_code == 200
    assert r.json() != {"detail": "WRONG API KEY - not authorized"}
