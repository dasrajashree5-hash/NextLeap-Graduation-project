"""Insight and theme read APIs."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Insight, Theme, Validation
from app.schemas.analysis_api import InsightResponse, ThemeResponse

router = APIRouter()


@router.get("", response_model=List[InsightResponse])
def list_insights(
    db: Session = Depends(get_db),
    limit: int = 50,
) -> List[InsightResponse]:
    rows = (
        db.query(Insight)
        .order_by(Insight.rank_score.desc().nullslast(), Insight.confidence_score.desc())
        .limit(limit)
        .all()
    )
    return [InsightResponse.model_validate(r, from_attributes=True) for r in rows]


@router.get("/{insight_id}", response_model=InsightResponse)
def get_insight(insight_id: int, db: Session = Depends(get_db)) -> InsightResponse:
    row = db.query(Insight).filter(Insight.id == insight_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Insight not found")
    return InsightResponse.model_validate(row, from_attributes=True)


@router.get("/{insight_id}/validations")
def insight_validations(insight_id: int, db: Session = Depends(get_db)):
    row = db.query(Insight).filter(Insight.id == insight_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Insight not found")
    vals = db.query(Validation).filter(Validation.insight_id == insight_id).all()
    return [
        {
            "source_type": v.source_type,
            "agreement": v.agreement,
            "notes": v.notes,
        }
        for v in vals
    ]
