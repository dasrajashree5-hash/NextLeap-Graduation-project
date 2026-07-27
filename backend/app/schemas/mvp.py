"""Pydantic schemas for MVP basket recommendations."""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

BarrierType = Literal[
    "awareness",
    "trust",
    "price",
    "search",
    "quality_doubt",
    "habit",
]


class BasketItem(BaseModel):
    name: str = Field(min_length=1, max_length=256)
    category: Optional[str] = None


class ProductSuggestion(BaseModel):
    product_id: str
    product_name: str
    category: str
    adjacent_to: str
    insight_id: int
    dominant_barrier: BarrierType
    message: str
    validation_status: Optional[str] = None
    price_inr: int
    rating: float


class BasketRecommendationResponse(BaseModel):
    customer_segment: str
    basket_categories: List[str]
    mvp_name: str
    suggestions: List[ProductSuggestion]


class RecommendRequest(BaseModel):
    basket_items: List[BasketItem] = Field(min_length=1, max_length=50)
    customer_segment: str = Field(default="mission_shopper", max_length=128)
    limit: int = Field(default=1, ge=1, le=5)


class CatalogProductResponse(BaseModel):
    product_id: str
    name: str
    category: str
    rating: float
    price_inr: int
    review_count: int


class MvpStatusResponse(BaseModel):
    mvp_name: str
    insight_count: int
    opportunity_count: int
    eval_basket_count: int
    ready: bool


class EvalBasketItem(BaseModel):
    name: str
    category: Optional[str] = None


class EvalBasketCase(BaseModel):
    id: str
    customer_segment: str
    items: List[EvalBasketItem] = Field(min_length=1)
    expected_adjacent_categories: List[str] = Field(min_length=1)


class EvalCaseResult(BaseModel):
    case_id: str
    passed: bool
    suggested_category: Optional[str] = None
    insight_id: Optional[int] = None
    category_relevant: bool
    insight_cited: bool
    insight_non_rejected: bool
    message_present: bool
    notes: List[str] = Field(default_factory=list)


class EvalSummary(BaseModel):
    total_cases: int
    passed_cases: int
    pass_rate: float
    category_hit_rate: float
    insight_citation_rate: float
    non_rejected_insight_rate: float


class EvaluateRequest(BaseModel):
    limit: int = Field(default=1, ge=1, le=5)
    basket_ids: Optional[List[str]] = None


class EvaluateResponse(BaseModel):
    summary: EvalSummary
    results: List[EvalCaseResult]
    run_id: Optional[int] = None
