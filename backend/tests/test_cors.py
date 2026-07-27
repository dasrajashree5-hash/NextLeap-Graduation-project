"""CORS must allow the deployed Netlify frontend, not just localhost."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

NETLIFY = "https://graduationprojectblinkitnextleap.netlify.app"
PREVIEW = "https://deploy-preview-3--graduationprojectblinkitnextleap.netlify.app"


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


@pytest.mark.parametrize("origin", [NETLIFY, PREVIEW, "http://localhost:3000"])
@pytest.mark.parametrize("path", ["/api/themes", "/api/insights"])
def test_preflight_allows_origin(client: TestClient, origin: str, path: str) -> None:
    res = client.options(
        path,
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert res.status_code == 200
    assert res.headers["access-control-allow-origin"] == origin


def test_unknown_origin_is_not_allowed(client: TestClient) -> None:
    res = client.options(
        "/api/themes",
        headers={
            "Origin": "https://malicious.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in res.headers
