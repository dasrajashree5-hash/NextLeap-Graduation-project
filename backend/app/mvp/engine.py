"""Smart basket expansion recommendation engine."""

from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models import Insight, Opportunity
from app.mvp.adjacency import adjacent_categories
from app.mvp.barriers import resolve_dominant_barrier
from app.mvp.catalog import CatalogProduct, categories_in_basket, products_for_category
from app.mvp.messaging import compose_message
from app.schemas.mvp import BasketItem, BasketRecommendationResponse, ProductSuggestion

_REJECTED = frozenset({"rejected", "contradicting"})


def _insight_matches_category(insight: Insight, category: str) -> bool:
    blob = " ".join(
        filter(
            None,
            [insight.problem, insight.evidence, insight.opportunity, insight.business_impact],
        )
    ).lower()
    cat = category.lower()
    tokens = cat.replace("&", " ").split()
    if cat in blob:
        return True
    return any(t in blob for t in tokens if len(t) > 3)


def _segment_match(insight: Insight, segment: str) -> bool:
    if not segment:
        return True
    seg = (insight.customer_segment or "").lower()
    return segment.lower() in seg or seg in segment.lower()


def _score_insight(insight: Insight, category: str, segment: str) -> float:
    if insight.validation_status in _REJECTED:
        return -1.0
    score = insight.rank_score or insight.confidence_score or 0.0
    if _insight_matches_category(insight, category):
        score += 2.0
    if _segment_match(insight, segment):
        score += 0.5
    if insight.validation_status in ("validated", "partially_supported", "high_confidence"):
        score += 1.5
    if insight.example_review_ids:
        score += 0.3
    return score


def _pick_insight(
    db: Session,
    target_category: str,
    customer_segment: str,
) -> Optional[Insight]:
    insights = db.query(Insight).all()
    if not insights:
        return None

    ranked = sorted(
        insights,
        key=lambda i: _score_insight(i, target_category, customer_segment),
        reverse=True,
    )
    for ins in ranked:
        if _score_insight(ins, target_category, customer_segment) >= 0:
            return ins
    return ranked[0] if ranked else None


def _pick_product(category: str) -> Optional[CatalogProduct]:
    products = products_for_category(category)
    if not products:
        return None
    return max(products, key=lambda p: (p.rating, p.review_count))


def _mvp_opportunity_insight(db: Session) -> Optional[int]:
    top = (
        db.query(Opportunity)
        .filter(Opportunity.insight_id.isnot(None))
        .order_by(Opportunity.rank.asc())
        .first()
    )
    return top.insight_id if top else None


def recommend_for_basket(
    db: Session,
    *,
    basket_items: List[BasketItem],
    customer_segment: str = "mission_shopper",
    limit: int = 1,
) -> BasketRecommendationResponse:
    """Return adjacent-category suggestions with insight-linked, barrier-aware copy."""
    item_tuples: List[Tuple[str, Optional[str]]] = [
        (i.name, i.category) for i in basket_items
    ]
    basket_cats = categories_in_basket(item_tuples)
    if not basket_cats:
        basket_cats = ["Grocery"]

    candidates = adjacent_categories(basket_cats)
    suggestions: List[ProductSuggestion] = []
    used_categories: set[str] = set()

    for target in candidates:
        if len(suggestions) >= limit:
            break
        if target in used_categories:
            continue
        product = _pick_product(target)
        if not product:
            continue

        insight = _pick_insight(db, target, customer_segment)
        if insight is None:
            fallback_id = _mvp_opportunity_insight(db)
            if fallback_id:
                insight = db.query(Insight).filter(Insight.id == fallback_id).first()

        if insight is None or insight.id is None:
            continue

        adjacent_source = basket_cats[0]
        barrier = resolve_dominant_barrier(
            db,
            customer_segment=customer_segment,
            target_category=target,
            linked_insight=insight,
        )
        message = compose_message(
            product=product,
            dominant_barrier=barrier,
            adjacent_to=adjacent_source,
            insight=insight,
        )
        suggestions.append(
            ProductSuggestion(
                product_id=product.product_id,
                product_name=product.name,
                category=product.category,
                adjacent_to=adjacent_source,
                insight_id=insight.id,
                dominant_barrier=barrier,
                message=message,
                validation_status=insight.validation_status,
                price_inr=product.price_inr,
                rating=product.rating,
            )
        )
        used_categories.add(target)

    return BasketRecommendationResponse(
        customer_segment=customer_segment,
        basket_categories=basket_cats,
        mvp_name="AI Smart Basket Expansion",
        suggestions=suggestions,
    )
