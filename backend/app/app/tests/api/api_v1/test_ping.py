from fastapi.testclient import TestClient

from app.core.config import settings


def test_ping(client: TestClient) -> None:
    r = client.get(f"{settings.API_V1_STR}/ping/")
    assert r.status_code == 200
    assert r.json() == "pong!"
