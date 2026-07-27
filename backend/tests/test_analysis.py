"""Phase 4 unit tests."""

import json
import uuid

import pytest
from fastapi.testclient import TestClient

from app.insights.confidence import compute_confidence
from app.insights.ranking import business_impact_weight, rank_score
from app.llm.json_utils import validate_model
from app.main import create_app
from app.schemas.analysis import ReviewAnalysisOutput


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c


def test_analysis_status_endpoint(client):
    response = client.get("/api/pipeline/analysis-status")
    assert response.status_code == 200
    body = response.json()
    assert body["analysis_version"] == "1.0.0"
    assert "pending_analysis" in body


def test_review_analysis_schema_validation():
    payload = {
        "sentiment": "negative",
        "sentiment_intensity": 0.8,
        "emotion": "frustration",
        "complaint_category": "Delivery",
        "motivation": "quick groceries",
        "unmet_need": "faster delivery",
        "jtbd": "restock pantry same day",
        "shopping_behaviour": "mission-driven",
        "customer_segment": "urban professional",
        "discovery": {
            "mentions_non_grocery_category": True,
            "named_categories": ["snacks"],
            "discovery_barriers": ["trust"],
            "latent_cross_category_intent": True,
            "cross_category_detail": "wants beauty items",
        },
    }
    model = validate_model(json.dumps(payload), ReviewAnalysisOutput)
    assert model.discovery.latent_cross_category_intent is True


def test_ranking_heuristics():
    high = business_impact_weight("Improves category discovery and basket expansion")
    low = business_impact_weight("Minor UI tweak")
    assert high > low
    assert rank_score(0.8, "category discovery") > rank_score(0.8, "minor ui")


def test_analyze_reviews_mocked(client, monkeypatch):
    ext = f"an-{uuid.uuid4().hex}"
    client.post(
        "/api/reviews/manual",
        json={
            "source_name": f"analyze_{uuid.uuid4().hex[:6]}",
            "reviews": [{"text": "Great app but search is bad", "external_id": ext}],
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
    client.post(
        "/api/pipeline/preprocess",
        json={"limit": 100, "skip_translation": True, "skip_embeddings": False},
    )

    sample = ReviewAnalysisOutput(
        sentiment="negative",
        sentiment_intensity=0.7,
        emotion="annoyance",
        complaint_category="Search",
        motivation=None,
        unmet_need="find products",
        jtbd="buy groceries quickly",
        shopping_behaviour="browse",
        customer_segment="student",
        discovery={
            "mentions_non_grocery_category": False,
            "named_categories": [],
            "discovery_barriers": ["search"],
            "latent_cross_category_intent": False,
            "cross_category_detail": None,
        },
    )

    from app.db.session import SessionLocal
    from app.models import Review

    db = SessionLocal()
    try:
        target = db.query(Review).filter(Review.external_id == ext).first()
        assert target is not None
        target_id = target.id
    finally:
        db.close()

    async def fake_batch(reviews, settings, budget):
        return [(r, sample, None) for r in reviews if r.id == target_id]

    def fake_eligible(db_sess, version, force=False):
        q = db_sess.query(Review).filter(Review.external_id == ext)
        if not force:
            q = q.filter(
                (Review.analysis_version.is_(None)) | (Review.analysis_version != version)
            )
        return q

    monkeypatch.setattr("app.analysis.review._run_batch_async", fake_batch)
    monkeypatch.setattr("app.analysis.review._eligible_query", fake_eligible)

    result = client.post("/api/pipeline/analyze", json={"limit": 1})
    assert result.status_code == 200
    assert result.json()["stats"]["analyzed"] >= 1

    from app.db.session import SessionLocal
    from app.models import Review

    db = SessionLocal()
    try:
        row = db.query(Review).filter(Review.external_id == ext).first()
        assert row.analysis_version == "1.0.0"
        assert row.analysis is not None
        assert row.analysis.sentiment == "negative"
    finally:
        db.close()
