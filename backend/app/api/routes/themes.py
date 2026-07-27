"""Theme read API."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Theme
from app.schemas.analysis_api import ThemeResponse

router = APIRouter()


@router.get("", response_model=List[ThemeResponse])
def list_themes(db: Session = Depends(get_db)) -> List[ThemeResponse]:
    rows = db.query(Theme).order_by(Theme.review_count.desc()).all()
    return [ThemeResponse.model_validate(r, from_attributes=True) for r in rows]
