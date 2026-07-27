"""Resolve dominant discovery barrier for segment + target category."""

from __future__ import annotations

from collections import Counter
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Analysis, Insight, Interview, Review
from app.research.affinity import build_affinity_map
from app.schemas.analysis import DISCOVERY_BARRIERS

_BARRIER_THEME_MAP = {
    "Trust": "trust",
    "Recommendations": "trust",
    "Category Discovery": "awareness",
    "Shopping Habit": "habit",
    "Price": "price",
    "Search": "search",
}


def _normalize_barrier(raw: str) -> Optional[str]:
    key = raw.strip().lower().replace(" ", "_").replace("-", "_")
    if key in DISCOVERY_BARRIERS:
        return key
    aliases = {
        "quality": "quality_doubt",
        "quality_doubt": "quality_doubt",
        "awareness": "awareness",
    }
    return aliases.get(key)


def barrier_from_interviews(db: Session, segment: str, target_category: str) -> Optional[str]:
    segment_lower = (segment or "").lower()
    counts: Counter[str] = Counter()
    for iv in db.query(Interview).all():
        seg = (iv.participant_segment or "").lower()
        if segment_lower and segment_lower not in seg and seg not in segment_lower:
            continue
        coding = iv.coding_json or {}
        for b in coding.get("discovery_barriers") or []:
            norm = _normalize_barrier(str(b))
            if norm:
                counts[norm] += 1
        if iv.discovery_barriers:
            for part in iv.discovery_barriers.split(","):
                norm = _normalize_barrier(part)
                if norm:
                    counts[norm] += 1
    if not counts:
        return None
    # Non-grocery expansion: trust is common in research corpus
    if target_category in ("Pet Care", "Baby Care", "Electronics") and counts.get("trust", 0):
        return "trust"
    return counts.most_common(1)[0][0]


def barrier_from_reviews(db: Session, target_category: str) -> Optional[str]:
    """Aggregate discovery barriers from analysis.discovery_json on recent reviews."""
    counts: Counter[str] = Counter()
    rows = (
        db.query(Analysis)
        .join(Review, Review.id == Analysis.review_id)
        .filter(Analysis.discovery_json.isnot(None))
        .limit(500)
        .all()
    )
    for row in rows:
        disc = row.discovery_json or {}
        for b in disc.get("discovery_barriers") or []:
            norm = _normalize_barrier(str(b))
            if norm:
                counts[norm] += 1
        cats = [c.lower() for c in (disc.get("named_categories") or [])]
        if target_category.lower() in " ".join(cats):
            for b in disc.get("discovery_barriers") or []:
                norm = _normalize_barrier(str(b))
                if norm:
                    counts[norm] += 2
    if counts:
        return counts.most_common(1)[0][0]
    return None


def barrier_from_affinity(db: Session, target_category: str) -> Optional[str]:
    for group in build_affinity_map(db):
        if group["theme_category"] == target_category:
            barriers = group.get("discovery_barriers") or set()
            if barriers:
                norm = _normalize_barrier(str(next(iter(barriers))))
                return norm
        theme = _BARRIER_THEME_MAP.get(group["theme_category"])
        if theme and group["finding_count"] > 10:
            return theme
    return None


def resolve_dominant_barrier(
    db: Session,
    *,
    customer_segment: str,
    target_category: str,
    linked_insight: Optional[Insight] = None,
) -> str:
    # Interviews first — primary depth when reviews stay generic (key risk mitigation).
    for resolver in (
        lambda: barrier_from_interviews(db, customer_segment, target_category),
        lambda: barrier_from_reviews(db, target_category),
        lambda: barrier_from_affinity(db, target_category),
    ):
        hit = resolver()
        if hit:
            return hit

    if linked_insight:
        text = ((linked_insight.problem or "") + " " + (linked_insight.evidence or "")).lower()
        if "trust" in text or "review" in text:
            return "trust"
        if "price" in text or "expensive" in text:
            return "price"
        if "search" in text or "find" in text:
            return "search"
        if "habit" in text or "same" in text:
            return "habit"
        if "aware" in text or "discover" in text:
            return "awareness"

    if target_category in ("Pet Care", "Baby Care", "Electronics", "Health & Nutrition"):
        return "trust"
    return "habit"
