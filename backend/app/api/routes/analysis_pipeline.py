"""Analysis and insight pipeline routes."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.analysis.review import analysis_pending_count, run_review_analysis
from app.clustering.runner import run_clustering
from app.config import Settings, get_settings
from app.db.session import get_db
from app.insights.generator import run_insight_generation
from app.models import Insight, Review, Theme
from app.schemas.analysis_api import (
    AnalysisStatusResponse,
    AnalyzeRequest,
    ClusterRequest,
    InsightResponse,
    InsightsRequest,
    PipelineRunResponse,
    ThemeResponse,
)

router = APIRouter()


@router.get("/analysis-status", response_model=AnalysisStatusResponse)
def analysis_status(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> AnalysisStatusResponse:
    version = settings.analysis_version
    pending = analysis_pending_count(db, settings)
    analyzed = (
        db.query(Review)
        .filter(Review.analysis_version == version)
        .filter(Review.analysis_failed.is_(False))
        .count()
    )
    failed = db.query(Review).filter(Review.analysis_failed.is_(True)).count()
    return AnalysisStatusResponse(
        analysis_version=version,
        pending_analysis=pending,
        analyzed_reviews=analyzed,
        failed_analysis=failed,
        themes=db.query(Theme).count(),
        insights=db.query(Insight).count(),
    )


@router.post("/analyze", response_model=PipelineRunResponse)
def analyze_reviews(
    body: AnalyzeRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> PipelineRunResponse:
    result = run_review_analysis(
        db, limit=body.limit, force=body.force, settings=settings
    )
    return PipelineRunResponse(run_id=result["run_id"], stats=result["stats"])


@router.post("/cluster", response_model=PipelineRunResponse)
def cluster_reviews(
    body: ClusterRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> PipelineRunResponse:
    result = run_clustering(
        db,
        settings=settings,
        force=body.force,
        min_cluster_size=body.min_cluster_size,
    )
    return PipelineRunResponse(run_id=result["run_id"], stats=result["stats"])


@router.post("/insights", response_model=PipelineRunResponse)
def generate_insights(
    body: InsightsRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> PipelineRunResponse:
    result = run_insight_generation(
        db, settings=settings, replace=body.replace
    )
    return PipelineRunResponse(run_id=result["run_id"], stats=result["stats"])
