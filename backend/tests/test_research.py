"""Phase 5 research repository tests."""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.models import Insight, Interview
from app.research.coding import code_interview
from app.research.opportunity import run_opportunity_assessment
from app.research.triangulation import triangulate_insights


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c


def test_seed_and_list_interviews(client):
    response = client.post("/api/research/seed?code=true")
    assert response.status_code == 200
    body = response.json()
    assert body["interviews_loaded"] >= 5
    assert body["survey_rows_loaded"] > 0

    listing = client.get("/api/research/interviews")
    assert listing.status_code == 200
    assert len(listing.json()) >= 5


def test_survey_aggregate(client):
    client.post("/api/research/seed?code=true")
    agg = client.get("/api/research/surveys/aggregate")
    assert agg.status_code == 200
    items = agg.json()
    assert any(i["question_key"].startswith("Q5") for i in items)


def test_affinity_and_triangulation(client):
    client.post("/api/research/seed?code=true")
    aff = client.get("/api/research/affinity")
    assert aff.status_code == 200
    assert len(aff.json()) >= 1

    tri = client.post("/api/research/triangulate")
    assert tri.status_code == 200


def test_interview_coding_heuristic():
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        iv = Interview(
            participant_segment="test",
            transcript=(
                "I always search for the same snacks and never browse. "
                "Recommendations feel irrelevant and I don't trust new categories without reviews."
            ),
        )
        db.add(iv)
        db.commit()
        db.refresh(iv)
        out = code_interview(db, iv, use_llm=False)
        assert out.jtbd
        assert out.quotes
        assert iv.coding_json is not None
    finally:
        db.close()


def test_rejection_on_contradictory_insight():
    from pathlib import Path

    from app.db.session import SessionLocal
    from app.research.seed import seed_research

    db = SessionLocal()
    try:
        root = Path(__file__).resolve().parents[2]
        seed_research(db, root, code=True)

        insight = Insight(
            problem="Delivery delays are the primary reason users fail at category discovery on Blinkit",
            evidence="Reviews mention delivery",
            frequency=10,
            example_review_ids=[1],
            customer_segment="urban",
            business_impact="category discovery",
            opportunity="fix delivery",
            confidence_score=0.7,
            validation_status="weak",
        )
        db.add(insight)
        db.commit()

        result = triangulate_insights(db)
        updated = db.query(Insight).filter(Insight.id == insight.id).first()
        assert updated.validation_status == "rejected"
        assert result["stats"]["rejected"] >= 1
    finally:
        db.close()


def test_opportunity_ranking(client):
    client.post("/api/research/seed?code=true")
    opp = client.post("/api/research/opportunities")
    assert opp.status_code == 200
    top = client.get("/api/research/opportunities?limit=3")
    assert top.status_code == 200
    rows = top.json()
    assert len(rows) >= 1
    assert rows[0]["scoring_rationale"]


def test_problem_definition_generate(client):
    client.post("/api/research/seed?code=true")
    resp = client.post("/api/research/problem-definition/generate")
    assert resp.status_code == 200
    body = resp.json()
    assert "Problem Definition" in body["markdown"]
    assert body["path"].endswith("problem-definition.md")


def test_manual_interview_upload(client):
    payload = {
        "participant_segment": "Freelancer · 25-34",
        "transcript": "I use Blinkit weekly but only for vegetables. " * 3,
    }
    resp = client.post("/api/research/interviews", json=payload)
    assert resp.status_code == 200
    assert resp.json()["id"] > 0
