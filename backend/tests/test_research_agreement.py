"""Research triangulation agreement metrics."""

from pathlib import Path

from app.db.session import SessionLocal
from app.models import Insight
from app.research.metrics import research_agreement_rate
from app.research.seed import seed_research
from app.research.triangulation import triangulate_insights


def test_agreement_rate_after_seed_and_triangulation():
    db = SessionLocal()
    try:
        root = Path(__file__).resolve().parents[2]
        seed_research(db, root, code=True)

        insight = Insight(
            problem="Search and habit block discovery of new categories on Blinkit",
            evidence="Users repeat same basket",
            frequency=12,
            example_review_ids=[1],
            customer_segment="urban professional",
            business_impact="category discovery",
            opportunity="Improve search and habit-breaking prompts",
            confidence_score=0.65,
            validation_status="weak",
        )
        db.add(insight)
        db.commit()

        triangulate_insights(db)
        metrics = research_agreement_rate(db)
        assert metrics["total"] >= 1
        assert 0.0 <= metrics["agreement_rate"] <= 1.0
        assert metrics["supported_count"] + metrics["rejected_count"] <= metrics["total"]
    finally:
        db.close()
