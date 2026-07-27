"""Edge-case regression tests (see docs/edge-cases.md)."""

import io
import json
import uuid

import pytest
from pydantic import ValidationError as PydanticValidationError

from app.insights.generator import _valid_review_ids
from app.llm.json_utils import extract_json_text, validate_with_repair
from app.preprocessing.clean import clean_text
from app.preprocessing.spam import is_spam
from app.schemas.analysis import InsightDraft, ReviewAnalysisOutput


def test_whitespace_only_marked_spam_in_pipeline(client, mock_embeddings):
    ext = f"empty-{uuid.uuid4().hex}"
    resp = client.post(
        "/api/reviews/manual",
        json={
            "source_name": f"edge_empty_{uuid.uuid4().hex[:6]}",
            "reviews": [{"text": "   ", "external_id": ext}],
        },
    )
    assert resp.status_code == 200
    client.post(
        "/api/pipeline/preprocess",
        json={"limit": 10, "skip_translation": True, "skip_embeddings": True},
    )
    from app.db.session import SessionLocal
    from app.models import Review

    db = SessionLocal()
    try:
        row = db.query(Review).filter(Review.external_id == ext).first()
        assert row is not None
        assert row.is_spam is True
    finally:
        db.close()


def test_spam_empty_and_rating_only():
    assert is_spam("")[0] is True
    assert is_spam("*****")[0] is True


def test_duplicate_ingest_skipped(client):
    source = f"edge_dup_{uuid.uuid4().hex[:8]}"
    payload = {
        "source_name": source,
        "reviews": [{"text": "Duplicate edge case text", "external_id": "dup-1"}],
    }
    assert client.post("/api/reviews/manual", json=payload).json()["stats"]["stored"] == 1
    assert client.post("/api/reviews/manual", json=payload).json()["stats"]["skipped"] == 1


def test_corrupted_csv_row_report(client):
    csv_body = "text,rating\n,5\n"
    resp = client.post(
        "/api/reviews/upload",
        data={"format": "csv"},
        files={"file": ("bad.csv", io.BytesIO(csv_body.encode()), "text/csv")},
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "validation_error"


def test_llm_json_fence_extraction():
    raw = 'Here is JSON:\n```json\n{"sentiment": "neutral", "sentiment_intensity": 0.5, '
    raw += '"emotion": "calm", "discovery": {"mentions_non_grocery_category": false, '
    raw += '"named_categories": [], "discovery_barriers": [], '
    raw += '"latent_cross_category_intent": false, "cross_category_detail": null}}\n```'
    parsed = json.loads(extract_json_text(raw))
    model = ReviewAnalysisOutput.model_validate(parsed)
    assert model.sentiment == "neutral"


def test_llm_missing_fields_repair_then_fail():
    broken = '{"sentiment": "positive"}'

    def repair_fn(raw: str, error: str) -> str:
        return broken

    model, err = validate_with_repair(broken, ReviewAnalysisOutput, repair_fn=repair_fn)
    assert model is None
    assert err


def test_insight_requires_cited_review_ids():
    with pytest.raises(PydanticValidationError):
        InsightDraft(
            problem="p",
            evidence="e",
            frequency=1,
            example_review_ids=[],
            customer_segment="s",
            business_impact="b",
            opportunity="o",
            confidence_score=0.5,
        )



def test_valid_review_ids_filters_hallucinated():
    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def all(self):
            return [(1,), (2,)]

    class FakeDB:
        def query(self, model):
            return FakeQuery()

    assert _valid_review_ids(FakeDB(), [1, 99, 2, 100]) == [1, 2]


def test_unicode_nfkc_cleaning():
    assert "fi" in clean_text("ﬁx delivery") or clean_text("ﬁx delivery") == "fix delivery"


def test_mvp_eval_without_insights(client):
    client.post("/api/research/seed?code=true")
    resp = client.post("/api/mvp/evaluate", json={"limit": 1})
    assert resp.status_code in (200, 422)
