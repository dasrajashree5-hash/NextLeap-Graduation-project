"""Business impact weighting for insight ranking."""

from __future__ import annotations

import re

_NORTH_STAR_TERMS = re.compile(
    r"\b(discovery|category|basket|cross-?sell|adjacent|expand|north star|"
    r"retention|ltv|order value|aov|items per order)\b",
    re.I,
)
_IMPACT_TERMS = re.compile(
    r"\b(revenue|growth|churn|conversion|engagement|margin)\b",
    re.I,
)


def business_impact_weight(text: str) -> float:
    if not text:
        return 0.5
    score = 0.5
    if _NORTH_STAR_TERMS.search(text):
        score += 0.35
    if _IMPACT_TERMS.search(text):
        score += 0.15
    return min(1.0, score)


def rank_score(confidence: float, business_impact: str) -> float:
    return round(confidence * business_impact_weight(business_impact), 4)
