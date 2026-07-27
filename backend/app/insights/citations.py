"""Mandatory review-ID citations for insights (hallucination guard)."""

from __future__ import annotations

from typing import Iterable, List, Sequence, Set

from sqlalchemy.orm import Session

from app.models import Review


def valid_review_ids(db: Session, ids: Sequence[int]) -> List[int]:
    if not ids:
        return []
    found: Set[int] = {
        row[0] for row in db.query(Review.id).filter(Review.id.in_(list(ids))).all()
    }
    return [i for i in ids if i in found]


def filter_citations(
    db: Session,
    cited: Iterable[int],
    *,
    allowed: Set[int] | None = None,
) -> List[int]:
    """Keep only IDs that exist in DB and (optionally) belong to the theme's review set."""
    raw = list(cited)
    if allowed is not None:
        raw = [i for i in raw if i in allowed]
    return valid_review_ids(db, raw)
