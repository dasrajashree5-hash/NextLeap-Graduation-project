"""Pydantic schemas for LLM analysis outputs."""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


DISCOVERY_BARRIERS = frozenset(
    {"awareness", "trust", "price", "search", "quality_doubt", "habit"}
)

THEME_CATEGORIES = [
    "Category Discovery",
    "Shopping Habit",
    "Price",
    "Search",
    "Recommendations",
    "Trust",
    "Delivery",
    "Availability",
    "Subscription",
    "Coupons",
]


class DiscoveryExtraction(BaseModel):
    mentions_non_grocery_category: bool = False
    named_categories: List[str] = Field(default_factory=list)
    discovery_barriers: List[str] = Field(default_factory=list)
    latent_cross_category_intent: bool = False
    cross_category_detail: Optional[str] = None


class ReviewAnalysisOutput(BaseModel):
    sentiment: Literal["positive", "neutral", "negative"]
    sentiment_intensity: float = Field(ge=0.0, le=1.0)
    emotion: str
    complaint_category: Optional[str] = None
    motivation: Optional[str] = None
    unmet_need: Optional[str] = None
    jtbd: Optional[str] = None
    shopping_behaviour: Optional[str] = None
    customer_segment: Optional[str] = None
    discovery: DiscoveryExtraction


class ClusterLabelOutput(BaseModel):
    label: str
    description: str
    category: str


class InsightDraft(BaseModel):
    problem: str
    evidence: str
    frequency: int = Field(ge=1)
    example_review_ids: List[int] = Field(min_length=1)
    customer_segment: str
    business_impact: str
    opportunity: str
    confidence_score: float = Field(ge=0.0, le=1.0)


class InsightListOutput(BaseModel):
    insights: List[InsightDraft]
