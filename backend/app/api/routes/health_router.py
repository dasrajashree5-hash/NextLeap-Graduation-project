"""Health check route."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.routes import health as health_checks
from app.config import Settings, get_settings
from app.db.session import get_db

router = APIRouter()


class DependencyStatus(BaseModel):
    status: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    environment: str
    database: DependencyStatus
    vector_store: DependencyStatus
    groq: DependencyStatus


@router.get("/health", response_model=HealthResponse)
async def health(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> HealthResponse:
    db_status, db_detail = health_checks.check_database(db)
    vec_status, vec_detail = health_checks.check_vector_store(settings)
    groq_status, groq_detail = await health_checks.check_groq(settings)

    checks = [db_status, vec_status]
    if groq_status == "ok":
        checks.append("ok")
    elif groq_status == "not_configured" and settings.environment == "development":
        pass
    else:
        checks.append(groq_status)

    overall = "ok" if all(c == "ok" for c in checks) and groq_status in (
        "ok",
        "not_configured",
    ) else "degraded"
    if db_status != "ok" or vec_status != "ok":
        overall = "error"
    if groq_status == "error":
        overall = "degraded" if db_status == "ok" and vec_status == "ok" else overall

    return HealthResponse(
        status=overall,
        environment=settings.environment,
        database=DependencyStatus(status=db_status, detail=db_detail),
        vector_store=DependencyStatus(status=vec_status, detail=vec_detail),
        groq=DependencyStatus(status=groq_status, detail=groq_detail),
    )
