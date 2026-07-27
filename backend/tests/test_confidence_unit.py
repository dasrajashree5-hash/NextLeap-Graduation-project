"""Confidence scoring unit tests."""

from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.insights.confidence import WEIGHTS, compute_confidence
from app.models import Analysis, Review, Source


def test_confidence_weights_sum_to_one():
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-6


def test_confidence_increases_with_frequency():
    db = SessionLocal()
    try:
        src = Source(name="conf_test_src", type="manual")
        db.add(src)
        db.flush()

        reviews = []
        for i in range(3):
            r = Review(
                source_id=src.id,
                external_id=f"conf-{i}",
                raw_text=f"review {i}",
                clean_text=f"review {i}",
                posted_at=datetime.now(timezone.utc),
            )
            db.add(r)
            reviews.append(r)
        db.flush()

        for r in reviews:
            db.add(
                Analysis(
                    review_id=r.id,
                    sentiment="negative",
                    status="success",
                )
            )
        db.commit()

        low = compute_confidence(db, [reviews[0].id], frequency=2)
        high = compute_confidence(db, [r.id for r in reviews], frequency=40)
        assert high["total"] > low["total"]
        assert "volume" in high["components"]
        assert high["weights"] == WEIGHTS
    finally:
        db.rollback()
        db.close()


def test_confidence_empty_review_ids():
    db = SessionLocal()
    try:
        out = compute_confidence(db, [], frequency=0)
        assert out["total"] == 0.0
        assert out["components"] == {}
    finally:
        db.close()
