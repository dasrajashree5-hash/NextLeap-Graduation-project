"""Per-review LLM analysis."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.llm.client import LLMRunBudget
from app.llm.groq_client import GroqClient, GroqLLMClient
from app.llm.json_utils import validate_with_repair
from app.llm.prompts import load_prompt_spec, render_prompt
from app.models import Analysis, Embedding, Review, Run
from app.schemas.analysis import ReviewAnalysisOutput

logger = logging.getLogger(__name__)

PROMPT_FILE = "review_analysis.v1.txt"
REPAIR_FILE = "json_repair.v1.txt"


def _analysis_text(review: Review) -> str:
    if review.translated_text:
        return review.translated_text
    return review.clean_text or review.raw_text


def _eligible_query(db: Session, version: str, force: bool):
    q = (
        db.query(Review)
        .join(Embedding, Embedding.review_id == Review.id)
        .filter(Review.is_spam.is_(False))
        .filter(Review.is_duplicate.is_(False))
    )
    if not force:
        q = q.filter(
            (Review.analysis_version.is_(None)) | (Review.analysis_version != version)
        )
    return q.order_by(Review.id)


def analysis_pending_count(db: Session, settings: Optional[Settings] = None) -> int:
    settings = settings or get_settings()
    return _eligible_query(db, settings.analysis_version, force=False).count()


async def _analyze_one(
    client: GroqLLMClient,
    review: Review,
    prompt_template: str,
    model: str,
    prompt_hash: str,
    repair_template: str,
    sync_client: GroqClient,
) -> Tuple[Review, Optional[ReviewAnalysisOutput], Optional[str]]:
    text = _analysis_text(review)
    rating = review.rating if review.rating is not None else "unknown"
    prompt = render_prompt(prompt_template, text=text, rating=rating)

    def repair_fn(raw: str, error: str) -> str:
        repair_prompt = render_prompt(repair_template, error=error, payload=raw[:4000])
        return sync_client.complete(repair_prompt, max_tokens=1024)

    try:
        raw = await client.complete(
            prompt,
            model=model,
            max_tokens=800,
            cache_key=f"{review.id}:{text[:200]}",
            prompt_hash=prompt_hash,
        )
        parsed, err = validate_with_repair(raw, ReviewAnalysisOutput, repair_fn=repair_fn)
        if parsed is None:
            return review, None, err
        return review, parsed, None
    except Exception as exc:  # noqa: BLE001
        return review, None, str(exc)


async def _run_batch_async(
    reviews: List[Review],
    settings: Settings,
    budget: LLMRunBudget,
) -> List[Tuple[Review, Optional[ReviewAnalysisOutput], Optional[str]]]:
    spec = load_prompt_spec(PROMPT_FILE)
    repair_spec = load_prompt_spec(REPAIR_FILE)
    model = spec.model or settings.groq_analysis_model
    client = GroqLLMClient(
        settings,
        budget=budget,
        max_concurrency=settings.llm_max_concurrency,
    )
    sync_client = GroqClient(settings)
    tasks = [
        _analyze_one(
            client,
            r,
            spec.body,
            model,
            spec.content_hash,
            repair_spec.body,
            sync_client,
        )
        for r in reviews
    ]
    return await asyncio.gather(*tasks)


def persist_analysis(
    db: Session,
    review: Review,
    output: ReviewAnalysisOutput,
    *,
    model_version: str,
    prompt_version: str,
    analysis_version: str,
) -> None:
    row = review.analysis
    if row is None:
        row = Analysis(review_id=review.id)
        db.add(row)
    row.sentiment = output.sentiment
    row.sentiment_intensity = output.sentiment_intensity
    row.emotion = output.emotion
    row.complaint_category = output.complaint_category
    row.shopping_behaviour = output.shopping_behaviour
    row.discovery_json = output.discovery.model_dump()
    row.jtbd = output.jtbd
    row.segment = output.customer_segment
    row.unmet_need = output.unmet_need
    row.motivation = output.motivation
    row.model_version = model_version
    row.prompt_version = prompt_version
    row.status = "success"
    review.analysis_failed = False
    review.analysis_version = analysis_version


def run_review_analysis(
    db: Session,
    limit: int = 100,
    force: bool = False,
    settings: Optional[Settings] = None,
) -> Dict[str, Any]:
    settings = settings or get_settings()
    version = settings.analysis_version
    spec = load_prompt_spec(PROMPT_FILE)
    model_version = spec.model or settings.groq_analysis_model

    run = Run(phase="analyze", status="running")
    db.add(run)
    db.commit()
    db.refresh(run)

    stats: Dict[str, Any] = {
        "analyzed": 0,
        "failed": 0,
        "skipped": 0,
        "cost_usd": 0.0,
    }

    try:
        pending = _eligible_query(db, version, force=force).limit(limit).all()
        if not pending:
            run.status = "completed"
            run.stats_json = stats
            run.finished_at = datetime.now(timezone.utc)
            db.commit()
            return {"run_id": run.id, "stats": stats}

        budget = LLMRunBudget(ceiling_usd=settings.llm_run_cost_ceiling_usd)
        results = asyncio.run(_run_batch_async(pending, settings, budget))

        for review, output, err in results:
            if output is None:
                review.analysis_failed = True
                review.analysis_version = version
                stats["failed"] += 1
                logger.warning("analysis failed review=%s: %s", review.id, err)
                continue
            persist_analysis(
                db,
                review,
                output,
                model_version=model_version,
                prompt_version=spec.version_tag,
                analysis_version=version,
            )
            stats["analyzed"] += 1

        stats["cost_usd"] = round(budget.spent_usd, 4)
        run.cost_estimate = budget.spent_usd
        run.status = "completed"
        run.stats_json = stats
        run.finished_at = datetime.now(timezone.utc)
        db.commit()
        return {"run_id": run.id, "stats": stats}

    except Exception as exc:  # noqa: BLE001
        run.status = "failed"
        run.error = str(exc)
        run.finished_at = datetime.now(timezone.utc)
        db.commit()
        raise
