"""End-to-end pipeline on fixed fixtures (mocked LLM + embeddings)."""

import io
import uuid
from pathlib import Path

from app.schemas.analysis import ReviewAnalysisOutput

FIXTURE_CSV = (
    Path(__file__).resolve().parent / "fixtures" / "prompt_golden" / "integration_reviews.csv"
)


def test_fixture_ingest_preprocess_analyze(client, mock_embeddings, monkeypatch):
    assert FIXTURE_CSV.is_file()
    source = f"integration_{uuid.uuid4().hex[:8]}"
    upload = client.post(
        "/api/reviews/upload",
        data={"format": "csv", "source_name": source},
        files={"file": ("integration.csv", FIXTURE_CSV.read_bytes(), "text/csv")},
    )
    assert upload.status_code == 200
    stored = upload.json()["stats"]["stored"]
    assert stored >= 5

    pre = client.post(
        "/api/pipeline/preprocess",
        json={"limit": 500, "skip_translation": True, "skip_embeddings": False},
    )
    assert pre.status_code == 200
    assert pre.json()["stats"]["processed"] >= 5

    sample = ReviewAnalysisOutput(
        sentiment="neutral",
        sentiment_intensity=0.5,
        emotion="neutral",
        complaint_category=None,
        motivation=None,
        unmet_need=None,
        jtbd="buy groceries",
        shopping_behaviour="routine",
        customer_segment="general",
        discovery={
            "mentions_non_grocery_category": False,
            "named_categories": [],
            "discovery_barriers": [],
            "latent_cross_category_intent": False,
            "cross_category_detail": None,
        },
    )

    async def fake_batch(reviews, settings, budget):
        return [(r, sample, None) for r in reviews]

    monkeypatch.setattr("app.analysis.review._run_batch_async", fake_batch)

    analyzed = client.post("/api/pipeline/analyze", json={"limit": stored + 5})
    assert analyzed.status_code == 200
    assert analyzed.json()["stats"]["analyzed"] >= 5

    status = client.get("/api/pipeline/analysis-status")
    assert status.status_code == 200
    assert status.json()["analyzed_reviews"] >= 5
