"""Explainable insight confidence scoring."""

from __future__ import annotations

import math
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models import Review, Source

WEIGHTS = {
    "volume": 0.25,
    "cross_source": 0.20,
    "coherence": 0.20,
    "sentiment_consistency": 0.20,
    "recency": 0.15,
}


def _entropy(counter: Counter) -> float:
    total = sum(counter.values())
    if total == 0:
        return 0.0
    ent = 0.0
    for count in counter.values():
        p = count / total
        if p > 0:
            ent -= p * math.log2(p)
    max_ent = math.log2(len(counter)) if len(counter) > 1 else 1.0
    if max_ent == 0:
        return 0.0
    return ent / max_ent


def compute_confidence(
    db: Session,
    review_ids: List[int],
    frequency: int,
    coherence_score: Optional[float] = None,
) -> Dict[str, Any]:
    reviews = db.query(Review).filter(Review.id.in_(review_ids)).all()
    if not reviews:
        return {"total": 0.0, "components": {}, "weights": WEIGHTS}

    volume = min(1.0, math.log10(frequency + 1) / 2.0)

    source_ids = {r.source_id for r in reviews}
    total_sources = db.query(Source).count()
    cross_source = len(source_ids) / max(1, total_sources)

    coherence = coherence_score if coherence_score is not None else 0.5

    sentiments = Counter(
        (r.analysis.sentiment if r.analysis and r.analysis.sentiment else "unknown")
        for r in reviews
    )
    sentiment_consistency = 1.0 - _entropy(sentiments)

    dated = [r.posted_at for r in reviews if r.posted_at]
    corpus_dates = [
        row[0]
        for row in db.query(Review.posted_at)
        .filter(Review.posted_at.isnot(None))
        .all()
    ]
    if dated and corpus_dates:
        newest = max(corpus_dates)
        oldest = min(corpus_dates)
        span = (newest - oldest).total_seconds() or 1.0
        recency_vals = [
            (newest - d).total_seconds() / span for d in dated
        ]
        recency = 1.0 - sum(recency_vals) / len(recency_vals)
        recency = max(0.0, min(1.0, recency))
    else:
        recency = 0.5

    components = {
        "volume": round(volume, 4),
        "cross_source": round(cross_source, 4),
        "coherence": round(coherence, 4),
        "sentiment_consistency": round(sentiment_consistency, 4),
        "recency": round(recency, 4),
    }
    total = sum(WEIGHTS[k] * components[k] for k in WEIGHTS)
    return {
        "total": round(total, 4),
        "components": components,
        "weights": WEIGHTS,
    }
