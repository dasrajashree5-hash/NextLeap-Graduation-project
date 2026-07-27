"""Review collection and upload routes."""

import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.collectors.base import RawReview
from app.collectors.csv_collector import CsvReviewCollector
from app.collectors.json_collector import JsonReviewCollector
from app.collectors.registry import get_store_collector
from app.core.errors import ValidationError
from app.db.session import get_db
from app.models import Review, Run, Source
from app.schemas.reviews import (
    AppStoreIngestRequest,
    IngestResponse,
    ManualReviewRequest,
    PlayStoreIngestRequest,
    ReviewStatsResponse,
    RunSummary,
)
from app.services import ingestion

router = APIRouter()


@router.post("/ingest/play-store", response_model=IngestResponse)
def ingest_play_store(
    body: PlayStoreIngestRequest,
    db: Session = Depends(get_db),
) -> IngestResponse:
    run = ingestion.start_run(db)
    try:
        collector = get_store_collector("play_store")
        config = body.model_dump()
        items = collector.fetch(config)
        source = ingestion.get_or_create_source(
            db,
            name=f"Play Store — {body.app_id}",
            source_type="play_store",
            config=config,
        )
        stats = ingestion.persist_reviews(db, source, items, run)
        return IngestResponse(run_id=run.id, stats=stats)
    except Exception as exc:  # noqa: BLE001
        ingestion.fail_run(db, run, str(exc))
        raise


@router.post("/ingest/app-store", response_model=IngestResponse)
def ingest_app_store(
    body: AppStoreIngestRequest,
    db: Session = Depends(get_db),
) -> IngestResponse:
    run = ingestion.start_run(db)
    try:
        collector = get_store_collector("app_store")
        config = body.model_dump()
        items = collector.fetch(config)
        source = ingestion.get_or_create_source(
            db,
            name=f"App Store — {body.app_id}",
            source_type="app_store",
            config=config,
        )
        stats = ingestion.persist_reviews(db, source, items, run)
        return IngestResponse(run_id=run.id, stats=stats)
    except Exception as exc:  # noqa: BLE001
        ingestion.fail_run(db, run, str(exc))
        raise


@router.post("/upload", response_model=IngestResponse)
async def upload_reviews(
    file: UploadFile = File(...),
    format: str = Form("csv"),
    source_name: str = Form("file_upload"),
    column_map_json: Optional[str] = Form(None),
    db: Session = Depends(get_db),
) -> IngestResponse:
    content = await file.read()
    column_map: Dict[str, str] = {}
    if column_map_json:
        try:
            column_map = json.loads(column_map_json)
        except json.JSONDecodeError as exc:
            raise ValidationError("Invalid column_map_json", details=[{"error": str(exc)}])

    fmt = format.lower()
    warnings: List[Dict[str, Any]] = []
    if fmt == "csv":
        collector = CsvReviewCollector()
        items, errors = collector.parse(content, column_map=column_map)
        if errors:
            raise ValidationError("CSV validation failed", details=errors)
        source_type = "csv"
    elif fmt == "json":
        collector = JsonReviewCollector()
        items, errors = collector.parse(content, column_map=column_map)
        if errors:
            raise ValidationError("JSON validation failed", details=errors)
        source_type = "json"
    else:
        raise ValidationError("format must be csv or json", details=[])

    run = ingestion.start_run(db)
    source = ingestion.get_or_create_source(
        db,
        name=source_name,
        source_type=source_type,
        config={"filename": file.filename, "column_map": column_map},
    )
    stats = ingestion.persist_reviews(db, source, items, run)
    return IngestResponse(run_id=run.id, stats=stats, warnings=warnings or None)


@router.post("/manual", response_model=IngestResponse)
def manual_reviews(
    body: ManualReviewRequest,
    db: Session = Depends(get_db),
) -> IngestResponse:
    items = [
        RawReview(
            text=item.text,
            external_id=item.external_id,
            rating=item.rating,
            raw_payload=item.model_dump(),
        )
        for item in body.reviews
    ]
    run = ingestion.start_run(db)
    source = ingestion.get_or_create_source(
        db,
        name=body.source_name,
        source_type="manual",
        config={},
    )
    stats = ingestion.persist_reviews(db, source, items, run)
    return IngestResponse(run_id=run.id, stats=stats)


@router.get("/stats", response_model=ReviewStatsResponse)
def review_stats(db: Session = Depends(get_db)) -> ReviewStatsResponse:
    total = db.query(func.count(Review.id)).scalar() or 0
    rows = (
        db.query(Source.name, Source.type, func.count(Review.id))
        .join(Review, Review.source_id == Source.id)
        .group_by(Source.id)
        .all()
    )
    by_source = [
        {"name": name, "type": stype, "count": count} for name, stype, count in rows
    ]
    return ReviewStatsResponse(total_reviews=total, by_source=by_source)


@router.get("/runs", response_model=List[RunSummary])
def list_runs(db: Session = Depends(get_db), limit: int = 20) -> List[RunSummary]:
    runs = db.query(Run).order_by(Run.id.desc()).limit(limit).all()
    return [
        RunSummary(
            id=r.id,
            phase=r.phase,
            status=r.status,
            stats_json=r.stats_json,
            error=r.error,
        )
        for r in runs
    ]
