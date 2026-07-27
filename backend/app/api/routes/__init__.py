"""API route aggregation."""

from fastapi import APIRouter

from app.api.routes.analysis_pipeline import router as analysis_pipeline_router
from app.api.routes.health_router import router as health_router
from app.api.routes.insights import router as insights_router
from app.api.routes.pipeline import router as pipeline_router
from app.api.routes.reviews import router as reviews_router
from app.api.routes.mvp import router as mvp_router
from app.api.routes.project import router as project_router
from app.api.routes.research import router as research_router
from app.api.routes.themes import router as themes_router

router = APIRouter()
router.include_router(health_router)
router.include_router(reviews_router, prefix="/reviews", tags=["reviews"])
router.include_router(pipeline_router, prefix="/pipeline", tags=["pipeline"])
router.include_router(analysis_pipeline_router, prefix="/pipeline", tags=["analysis"])
router.include_router(insights_router, prefix="/insights", tags=["insights"])
router.include_router(themes_router, prefix="/themes", tags=["themes"])
router.include_router(research_router, prefix="/research", tags=["research"])
router.include_router(project_router)
router.include_router(mvp_router, prefix="/mvp", tags=["mvp"])
