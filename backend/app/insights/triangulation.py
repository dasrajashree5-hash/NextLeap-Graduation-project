"""Cross-source triangulation labels."""

from __future__ import annotations

from collections import Counter
from typing import List, Tuple

from sqlalchemy.orm import Session

from app.models import Review, Source


def triangulation_label(
    db: Session,
    review_ids: List[int],
) -> Tuple[str, str]:
    """Returns (agreement, notes)."""
    reviews = db.query(Review).filter(Review.id.in_(review_ids)).all()
    if not reviews:
        return "weak", "No cited reviews"

    source_types: Counter[str] = Counter()
    sentiments: Counter[str] = Counter()
    for r in reviews:
        src = db.query(Source).filter(Source.id == r.source_id).first()
        source_types[src.type if src else "unknown"] += 1
        sent = r.analysis.sentiment if r.analysis and r.analysis.sentiment else "unknown"
        sentiments[sent] += 1

    num_sources = len(source_types)
    total = sum(sentiments.values())
    top_sent = sentiments.most_common(1)[0][1] if sentiments else 0
    agreement_ratio = top_sent / total if total else 0.0

    notes = (
        f"sources={dict(source_types)}; sentiment_agreement={agreement_ratio:.2f}"
    )

    if num_sources >= 3 and agreement_ratio >= 0.7:
        return "high_confidence", notes
    if num_sources >= 2 and agreement_ratio >= 0.55:
        return "consistent", notes
    if num_sources >= 2 and agreement_ratio < 0.4:
        return "contradicting", notes
    return "weak", notes
