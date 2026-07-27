"""Phase 2 review ingestion tests."""

import io
import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c


def test_manual_review_ingest(client):
    ext = f"manual-{uuid.uuid4().hex}"
    response = client.post(
        "/api/reviews/manual",
        json={
            "source_name": f"test_manual_{uuid.uuid4().hex[:8]}",
            "reviews": [{"text": "Great delivery speed", "rating": 5, "external_id": ext}],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["stats"]["stored"] == 1


def test_manual_dedupe(client):
    source = f"test_manual_dedupe_{uuid.uuid4().hex[:8]}"
    payload = {
        "source_name": source,
        "reviews": [{"text": "Same review text", "external_id": "ext-1"}],
    }
    first = client.post("/api/reviews/manual", json=payload)
    second = client.post("/api/reviews/manual", json=payload)
    assert first.json()["stats"]["stored"] == 1
    assert second.json()["stats"]["skipped"] == 1
    assert second.json()["stats"]["stored"] == 0


def test_csv_validation_errors(client):
    csv_body = "text,rating\n,5\n,not_a_number\n"
    response = client.post(
        "/api/reviews/upload",
        data={"format": "csv", "source_name": "bad_csv"},
        files={"file": ("bad.csv", io.BytesIO(csv_body.encode()), "text/csv")},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert "details" in body


def test_csv_missing_text_column(client):
    csv_body = "rating,author\n5,alice\n"
    response = client.post(
        "/api/reviews/upload",
        data={"format": "csv"},
        files={"file": ("bad.csv", io.BytesIO(csv_body.encode()), "text/csv")},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_csv_valid_upload(client):
    ext = f"r-{uuid.uuid4().hex[:8]}"
    csv_body = f"text,rating,external_id\nFast groceries,5,{ext}\n"
    response = client.post(
        "/api/reviews/upload",
        data={"format": "csv", "source_name": f"good_csv_{uuid.uuid4().hex[:8]}"},
        files={"file": ("good.csv", io.BytesIO(csv_body.encode()), "text/csv")},
    )
    assert response.status_code == 200
    assert response.json()["stats"]["stored"] >= 1


def test_review_stats(client):
    response = client.get("/api/reviews/stats")
    assert response.status_code == 200
    assert "total_reviews" in response.json()
