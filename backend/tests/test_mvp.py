"""Phase 6a — MVP recommendation engine tests."""

from unittest.mock import MagicMock

from app.db.session import SessionLocal
from app.mvp.adjacency import adjacent_categories
from app.mvp.catalog import CatalogProduct, infer_category
from app.mvp.engine import recommend_for_basket
from app.mvp.messaging import compose_message
from app.schemas.mvp import BasketItem


def test_infer_category_from_keywords():
    assert infer_category("Amul Taaza Milk 1L") == "Dairy"
    assert infer_category("Lay's chips") == "Snacks"


def test_adjacent_categories_excludes_basket():
    adj = adjacent_categories(["Dairy", "Grocery"])
    assert "Dairy" not in adj
    assert "Grocery" not in adj
    assert "Pet Care" in adj


def test_barrier_messaging_trust_vs_awareness():
    product = CatalogProduct(
        product_id="x",
        name="Test Treats",
        category="Pet Care",
        rating=4.5,
        price_inr=99,
        review_count=1000,
    )
    trust_msg = compose_message(
        product=product,
        dominant_barrier="trust",
        adjacent_to="Grocery",
        insight=None,
    )
    aware_msg = compose_message(
        product=product,
        dominant_barrier="awareness",
        adjacent_to="Grocery",
        insight=None,
    )
    assert "rated" in trust_msg.lower() or "review" in trust_msg.lower()
    assert "try" in aware_msg.lower() or "complete" in aware_msg.lower()
    assert trust_msg != aware_msg


def test_recommend_for_basket_links_insight(monkeypatch):
    db = SessionLocal()
    try:
        insight = MagicMock()
        insight.id = 4242
        insight.validation_status = "validated"
        insight.evidence = "Interview quotes cite trust before trying pet SKUs"
        insight.problem = "Pet Care discovery gap"
        insight.customer_segment = "mission_shopper"
        insight.rank_score = 1.0
        insight.confidence_score = 0.5
        insight.example_review_ids = [1]

        monkeypatch.setattr(
            "app.mvp.engine._pick_insight",
            lambda _db, _cat, _seg: insight,
        )

        result = recommend_for_basket(
            db,
            basket_items=[
                BasketItem(name="Amul Milk 1L"),
                BasketItem(name="Britannia bread"),
            ],
            customer_segment="mission_shopper",
            limit=1,
        )
        assert result.suggestions
        sug = result.suggestions[0]
        assert sug.insight_id == 4242
        assert sug.message
        assert "trust" in sug.message.lower() or "review" in sug.message.lower()
        assert sug.category not in result.basket_categories
    finally:
        db.close()
