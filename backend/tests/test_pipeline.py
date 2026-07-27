"""Pipeline API tests."""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c


def test_pipeline_status(client):
    response = client.get("/api/pipeline/status")
    assert response.status_code == 200
    body = response.json()
    assert "pending" in body
    assert body["preprocessing_version"] == "1.0.0"


def test_preprocess_idempotent(client, monkeypatch):
    ext = f"pre-{uuid.uuid4().hex}"
    client.post(
        "/api/reviews/manual",
        json={
            "source_name": f"preprocess_{uuid.uuid4().hex[:6]}",
            "reviews": [{"text": "Vegetables were fresh and delivery on time", "external_id": ext}],
        },
    )

    monkeypatch.setattr(
        "app.services.pipeline.encode_texts",
        lambda texts, batch_size=64: __import__("numpy").zeros((len(texts), 384), dtype="float32"),
    )
    monkeypatch.setattr(
        "app.services.pipeline.VectorStore",
        lambda settings: type(
            "MockStore",
            (),
            {
                "upsert": lambda *a, **k: None,
                "vector_ref": lambda self, rid: f"mock:{rid}",
                "count": lambda self: 0,
            },
        )(),
    )

    pending_before = client.get("/api/pipeline/status").json()["pending"]

    first = client.post(
        "/api/pipeline/preprocess",
        json={"limit": 5000, "skip_translation": True, "skip_embeddings": False},
    )
    assert first.status_code == 200
    assert first.json()["stats"]["processed"] >= 1

    from app.db.session import SessionLocal
    from app.models import Review

    db = SessionLocal()
    try:
        row = db.query(Review).filter(Review.external_id == ext).first()
        assert row is not None
        assert row.preprocessing_version == "1.0.0"
        assert row.clean_text
    finally:
        db.close()

    second = client.post(
        "/api/pipeline/preprocess",
        json={"limit": 5000, "skip_translation": True, "skip_embeddings": True},
    )
    assert second.status_code == 200
    assert second.json()["stats"]["processed"] == 0
    pending_after = client.get("/api/pipeline/status").json()["pending"]
    assert pending_after == 0
    assert pending_before >= 1
