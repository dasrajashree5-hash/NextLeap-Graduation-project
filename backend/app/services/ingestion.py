"""Persist collected reviews."""

import hashlib
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.collectors.base import RawReview
from app.models import Review, Run, Source


def _json_safe(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value


def _stable_external_id(review: RawReview) -> str:
    if review.external_id:
        return str(review.external_id)
    digest = hashlib.sha256(review.text.encode("utf-8")).hexdigest()
    return f"hash_{digest[:32]}"


def get_or_create_source(
    db: Session,
    name: str,
    source_type: str,
    config: Optional[Dict[str, Any]] = None,
) -> Source:
    existing = (
        db.query(Source)
        .filter(Source.name == name, Source.type == source_type)
        .first()
    )
    if existing:
        if config:
            existing.config_json = config
        return existing
    source = Source(name=name, type=source_type, config_json=config or {})
    db.add(source)
    db.flush()
    return source


def persist_reviews(
    db: Session,
    source: Source,
    items: List[RawReview],
    run: Run,
) -> Dict[str, int]:
    fetched = len(items)
    stored = 0
    skipped = 0

    for item in items:
        external_id = _stable_external_id(item)
        exists = (
            db.query(Review.id)
            .filter(Review.source_id == source.id, Review.external_id == external_id)
            .first()
        )
        if exists:
            skipped += 1
            continue

        payload = _json_safe(item.raw_payload if isinstance(item.raw_payload, dict) else {"raw": item.raw_payload})
        if not payload:
            payload = {"text": item.text}

        review = Review(
            source_id=source.id,
            external_id=external_id,
            raw_text=item.text,
            clean_text=None,
            rating=item.rating,
            language=None,
            translated_text=None,
            author_hash=item.author_hash,
            posted_at=item.posted_at,
            is_spam=False,
            is_duplicate=False,
            dedupe_hash=hashlib.sha256(item.text.strip().lower().encode()).hexdigest(),
            raw_payload=payload,
        )
        db.add(review)
        stored += 1

    stats = {
        "fetched": fetched,
        "stored": stored,
        "skipped": skipped,
        "source_id": source.id,
        "source_type": source.type,
    }
    run.stats_json = stats
    run.status = "completed"
    run.finished_at = datetime.now(timezone.utc)
    db.commit()
    return stats


def start_run(db: Session, phase: str = "ingest") -> Run:
    run = Run(phase=phase, status="running")
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def fail_run(db: Session, run: Run, message: str) -> None:
    run.status = "failed"
    run.error = message
    run.finished_at = datetime.now(timezone.utc)
    db.commit()
