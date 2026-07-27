"""Phase 6 MVP API and evaluation tests."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.mvp.evaluation import load_eval_baskets, run_evaluation
from app.db.session import SessionLocal
from app.models import Insight


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c


def test_mvp_status_and_catalog(client):
    status = client.get("/api/mvp/status")
    assert status.status_code == 200
    body = status.json()
    assert body["mvp_name"] == "AI Smart Basket Expansion"
    assert body["eval_basket_count"] >= 1

    catalog = client.get("/api/mvp/catalog")
    assert catalog.status_code == 200
    assert len(catalog.json()) >= 5


def test_recommend_endpoint(client):
    status = client.get("/api/mvp/status").json()
    if not status["ready"]:
        pytest.skip("No insights in database")

    resp = client.post(
        "/api/mvp/recommend",
        json={
            "basket_items": [
                {"name": "Amul Milk 1L"},
                {"name": "Britannia bread"},
            ],
            "customer_segment": "mission_shopper",
            "limit": 1,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["suggestions"]
    sug = data["suggestions"][0]
    assert sug["insight_id"]
    assert sug["message"]
    assert sug["category"] not in data["basket_categories"]


def test_recommend_empty_basket_rejected(client):
    resp = client.post(
        "/api/mvp/recommend",
        json={"basket_items": [], "customer_segment": "mission_shopper"},
    )
    assert resp.status_code == 422


def test_eval_baskets_list(client):
    resp = client.get("/api/mvp/eval-baskets")
    assert resp.status_code == 200
    rows = resp.json()
    assert rows[0]["id"]
    assert "expected_adjacent_categories" not in rows[0]


def test_evaluation_harness():
    db = SessionLocal()
    try:
        if db.query(Insight).count() == 0:
            db.add(
                Insight(
                    problem="Cross-category discovery from grocery baskets",
                    evidence="Validated interview theme",
                    frequency=5,
                    example_review_ids=[1],
                    validation_status="validated",
                    rank_score=5.0,
                )
            )
            db.commit()
        payload = run_evaluation(db, limit=1, record_run=False)
        assert payload["summary"].total_cases == len(load_eval_baskets())
        assert payload["summary"].category_hit_rate >= 0.0
        assert len(payload["results"]) == payload["summary"].total_cases
    finally:
        db.close()


def test_evaluate_endpoint(client):
    if not client.get("/api/mvp/status").json().get("ready"):
        pytest.skip("No insights in database")
    resp = client.post("/api/mvp/evaluate", json={"limit": 1})
    assert resp.status_code == 200
    body = resp.json()
    assert body["summary"]["total_cases"] >= 1
    assert body["run_id"] is not None
