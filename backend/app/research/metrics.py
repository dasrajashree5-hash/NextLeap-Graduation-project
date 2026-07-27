"""Research validation metrics."""

from __future__ import annotations

from typing import Any, Dict

from sqlalchemy.orm import Session

from app.models import Insight

_SUPPORTED = frozenset({"validated", "partially_supported", "high_confidence"})
_REJECTED = frozenset({"rejected"})


def research_agreement_rate(db: Session) -> Dict[str, Any]:
    """
    Share of AI insights aligned with human research after triangulation.

    Agreement = validated or partially_supported (or legacy high_confidence).
    """
    insights = db.query(Insight).all()
    total = len(insights)
    if total == 0:
        return {
            "agreement_rate": 0.0,
            "supported_count": 0,
            "rejected_count": 0,
            "total": 0,
        }

    supported = sum(
        1 for i in insights if (i.validation_status or "") in _SUPPORTED
    )
    rejected = sum(
        1 for i in insights if (i.validation_status or "") in _REJECTED
    )
    return {
        "agreement_rate": round(supported / total, 4),
        "supported_count": supported,
        "rejected_count": rejected,
        "total": total,
    }
