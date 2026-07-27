"""Prompt golden-set regression (no live LLM in default CI)."""

import json
import os
from pathlib import Path

import pytest

from app.llm.json_utils import validate_model
from app.schemas.analysis import ReviewAnalysisOutput
from app.testing.prompt_agreement import batch_agreement, weighted_agreement

GOLDEN_PATH = Path(__file__).resolve().parent / "fixtures" / "prompt_golden" / "review_golden_set.json"
MIN_GOLDEN_AGREEMENT = 0.95
MIN_GOLDEN_COUNT = 50


def _load_golden():
    data = json.loads(GOLDEN_PATH.read_text())
    assert len(data) >= MIN_GOLDEN_COUNT, f"golden set needs >={MIN_GOLDEN_COUNT} rows"
    return data


def test_golden_set_size_and_schema():
    rows = _load_golden()
    for row in rows:
        assert "text" in row and row["text"].strip()
        assert "expected" in row
        assert "baseline_output" in row
        payload = json.dumps(row["baseline_output"])
        model = validate_model(payload, ReviewAnalysisOutput)
        assert model.sentiment in ("positive", "neutral", "negative")


def test_golden_baseline_agreement_floor():
    rows = _load_golden()
    summary = batch_agreement(rows)
    assert summary["mean"] >= MIN_GOLDEN_AGREEMENT, summary


def test_golden_per_row_self_consistency():
    rows = _load_golden()
    for row in rows[:10]:
        expected = {
            **row["expected"],
            "discovery": {
                "discovery_barriers": row["expected"].get("discovery_barriers", []),
                "mentions_non_grocery_category": row["expected"].get(
                    "mentions_non_grocery_category", False
                ),
            },
        }
        score = weighted_agreement(expected, row["baseline_output"])
        assert score >= MIN_GOLDEN_AGREEMENT


@pytest.mark.live_llm
def test_live_llm_sample(client, monkeypatch):
    if not os.getenv("GROQ_API_KEY"):
        pytest.skip("GROQ_API_KEY not set")

    from app.analysis.review import _run_batch_async
    from app.config import get_settings
    from app.db.session import SessionLocal
    from app.llm.client import LLMRunBudget
    from app.models import Review

    row = _load_golden()[0]
    ext = f"live-{row['id']}"
    client.post(
        "/api/reviews/manual",
        json={
            "source_name": "live_llm_sample",
            "reviews": [{"text": row["text"], "rating": row.get("rating"), "external_id": ext}],
        },
    )

    db = SessionLocal()
    try:
        review = db.query(Review).filter(Review.external_id == ext).first()
        assert review is not None
        settings = get_settings()
        budget = LLMRunBudget(ceiling_usd=0.05)
        results = __import__("asyncio").run(
            _run_batch_async([review], settings, budget)
        )
        assert results[0][1] is not None
    finally:
        db.close()
