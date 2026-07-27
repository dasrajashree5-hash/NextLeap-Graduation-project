"""Preprocessing pipeline routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db.session import get_db
from app.embeddings.store import VectorStore
from app.schemas.pipeline import (
    PipelineStatusResponse,
    PreprocessRequest,
    PreprocessResponse,
)
from app.services import pipeline as pipeline_service

router = APIRouter()


@router.get("/status", response_model=PipelineStatusResponse)
def pipeline_status(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> PipelineStatusResponse:
    status = pipeline_service.pipeline_status(db, settings)
    chroma_count = None
    try:
        chroma_count = VectorStore(settings).count()
    except Exception:  # noqa: BLE001
        chroma_count = None
    return PipelineStatusResponse(
        preprocessing_version=status["preprocessing_version"],
        total_reviews=status["total_reviews"],
        pending=status["pending"],
        embedded=status["embedded"],
        chroma_vectors=chroma_count,
    )


@router.post("/preprocess", response_model=PreprocessResponse)
def preprocess_reviews(
    body: PreprocessRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> PreprocessResponse:
    result = pipeline_service.run_preprocess_pipeline(
        db,
        limit=body.limit,
        force=body.force,
        settings=settings,
        skip_translation=body.skip_translation,
        skip_embeddings=body.skip_embeddings,
    )
    return PreprocessResponse(run_id=result["run_id"], stats=result["stats"])
