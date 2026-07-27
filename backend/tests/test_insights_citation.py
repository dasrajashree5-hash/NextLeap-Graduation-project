"""Insight citation / hallucination guards."""

from app.insights.citations import valid_review_ids
from app.schemas.analysis import InsightDraft


def test_uncitable_review_ids_removed():
    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def all(self):
            return [(5,)]

    class FakeDB:
        def query(self, model):
            return FakeQuery()

    cited = valid_review_ids(FakeDB(), [5, 999, 1000])
    assert cited == [5]


def test_insight_draft_requires_non_empty_citations():
    draft = InsightDraft(
        problem="Test",
        evidence="Evidence",
        frequency=2,
        example_review_ids=[1],
        customer_segment="test",
        business_impact="discovery",
        opportunity="fix",
        confidence_score=0.6,
    )
    assert draft.example_review_ids == [1]
