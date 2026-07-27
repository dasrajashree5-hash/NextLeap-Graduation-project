"""MVP Smart Basket Expansion API."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import ServiceUnavailableError, ValidationError
from app.db.session import get_db
from app.models import Insight, Opportunity
from app.mvp.catalog import PRODUCTS
from app.mvp.engine import recommend_for_basket
from app.mvp.evaluation import load_eval_baskets, run_evaluation
from app.schemas.mvp import (
    BasketRecommendationResponse,
    CatalogProductResponse,
    EvaluateRequest,
    EvaluateResponse,
    MvpStatusResponse,
    RecommendRequest,
)

router = APIRouter()


@router.get("/status", response_model=MvpStatusResponse)
def mvp_status(db: Session = Depends(get_db)) -> MvpStatusResponse:
    insight_n = db.query(Insight).count()
    opp_n = db.query(Opportunity).count()
    eval_n = len(load_eval_baskets())
    return MvpStatusResponse(
        mvp_name="AI Smart Basket Expansion",
        insight_count=insight_n,
        opportunity_count=opp_n,
        eval_basket_count=eval_n,
        ready=insight_n > 0,
    )


@router.get("/catalog", response_model=List[CatalogProductResponse])
def mvp_catalog() -> List[CatalogProductResponse]:
    return [
        CatalogProductResponse(
            product_id=p.product_id,
            name=p.name,
            category=p.category,
            rating=p.rating,
            price_inr=p.price_inr,
            review_count=p.review_count,
        )
        for p in PRODUCTS
    ]


@router.post("/recommend", response_model=BasketRecommendationResponse)
def recommend(
    body: RecommendRequest,
    db: Session = Depends(get_db),
) -> BasketRecommendationResponse:
    if db.query(Insight).count() == 0:
        raise ServiceUnavailableError(
            "No insights available. Run the analysis pipeline before requesting recommendations."
        )
    result = recommend_for_basket(
        db,
        basket_items=body.basket_items,
        customer_segment=body.customer_segment,
        limit=body.limit,
    )
    if not result.suggestions:
        raise ValidationError(
            "Could not generate a suggestion for this basket (no insight linkage or catalog match).",
            details=[{"basket_categories": result.basket_categories}],
        )
    return result


@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate_mvp(
    body: EvaluateRequest,
    db: Session = Depends(get_db),
) -> EvaluateResponse:
    try:
        payload = run_evaluation(
            db,
            limit=body.limit,
            basket_ids=body.basket_ids,
            record_run=True,
        )
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc
    return EvaluateResponse.model_validate(payload)


@router.get("/eval-baskets", response_model=List[dict])
def list_eval_baskets():
    """Held-out baskets used by the evaluation harness (no labels in recommend path)."""
    cases = load_eval_baskets()
    return [
        {
            "id": c.id,
            "customer_segment": c.customer_segment,
            "items": [i.model_dump() for i in c.items],
        }
        for c in cases
    ]
