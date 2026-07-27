import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "blinkit-discovery-engine"


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["database"]["status"] == "ok"
    assert body["vector_store"]["status"] == "ok"
    assert body["status"] in ("ok", "degraded")
