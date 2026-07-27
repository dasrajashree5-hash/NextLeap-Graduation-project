"""Insight generation from themes and analyses."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.insights.citations import filter_citations
from app.insights.confidence import compute_confidence
from app.insights.ranking import rank_score
from app.insights.triangulation import triangulation_label
from app.llm.client import LLMRunBudget
from app.llm.groq_client import GroqClient, GroqLLMClient
from app.llm.json_utils import validate_with_repair
from app.llm.prompts import load_prompt_spec, render_prompt
from app.models import Cluster, Insight, Review, ReviewTheme, Run, Theme, Validation
from app.schemas.analysis import InsightListOutput

logger = logging.getLogger(__name__)

PROMPT_FILE = "insight_generation.v1.txt"
REPAIR_FILE = "json_repair.v1.txt"


def _review_sample(db: Session, review_ids: List[int], limit: int = 8) -> str:
    rows = db.query(Review).filter(Review.id.in_(review_ids[:limit])).all()
    parts = []
    for r in rows:
        text = (r.translated_text or r.clean_text or r.raw_text)[:300]
        analysis = r.analysis
        summary = ""
        if analysis:
            summary = (
                f"sentiment={analysis.sentiment}, segment={analysis.segment}, "
                f"jtbd={analysis.jtbd}"
            )
        parts.append(f"[id={r.id}] {text}\n  analysis: {summary}")
    return "\n".join(parts)


async def _generate_for_theme(
    client: GroqLLMClient,
    db: Session,
    theme: Theme,
    cluster: Optional[Cluster],
    model: str,
    prompt_hash: str,
    repair_body: str,
    settings: Settings,
) -> Tuple[List[Dict[str, Any]], int]:
    link_rows = (
        db.query(ReviewTheme.review_id)
        .filter(ReviewTheme.theme_id == theme.id)
        .all()
    )
    review_ids = [r[0] for r in link_rows]
    if not review_ids:
        return [], 0

    spec = load_prompt_spec(PROMPT_FILE)
    prompt = render_prompt(
        spec.body,
        category=theme.category or "",
        label=theme.label,
        description=theme.description or "",
        review_ids=review_ids,
        samples=_review_sample(db, review_ids),
    )

    sync_client = GroqClient(settings)

    def repair_fn(raw: str, error: str) -> str:
        repair_prompt = render_prompt(repair_body, error=error, payload=raw[:4000])
        return sync_client.complete(repair_prompt, max_tokens=1200)

    raw = await client.complete(
        prompt, model=model, max_tokens=1500, prompt_hash=prompt_hash
    )
    parsed, err = validate_with_repair(raw, InsightListOutput, repair_fn=repair_fn)
    if parsed is None:
        logger.warning("insight generation failed theme=%s: %s", theme.id, err)
        return [], 0

    valid_set: Set[int] = set(review_ids)
    out: List[Dict[str, Any]] = []
    dropped_uncitable = 0
    for draft in parsed.insights:
        cited = filter_citations(
            db, draft.example_review_ids, allowed=valid_set
        )
        if not cited:
            dropped_uncitable += 1
            continue
        out.append(
            {
                "problem": draft.problem,
                "evidence": draft.evidence,
                "frequency": max(draft.frequency, len(cited)),
                "example_review_ids": cited,
                "customer_segment": draft.customer_segment,
                "business_impact": draft.business_impact,
                "opportunity": draft.opportunity,
                "theme_id": theme.id,
                "coherence": cluster.coherence_score if cluster else None,
            }
        )
    return out, dropped_uncitable


def run_insight_generation(
    db: Session,
    settings: Optional[Settings] = None,
    replace: bool = True,
) -> Dict[str, Any]:
    settings = settings or get_settings()
    run = Run(phase="insights", status="running")
    db.add(run)
    db.commit()
    db.refresh(run)

    stats: Dict[str, Any] = {"created": 0, "dropped": 0, "cost_usd": 0.0}

    try:
        if replace:
            db.query(Validation).delete()
            db.query(Insight).delete()
            db.flush()

        themes = db.query(Theme).all()
        if not themes:
            run.status = "completed"
            run.stats_json = {**stats, "message": "no themes"}
            run.finished_at = datetime.now(timezone.utc)
            db.commit()
            return {"run_id": run.id, "stats": run.stats_json}

        budget = LLMRunBudget(ceiling_usd=settings.llm_run_cost_ceiling_usd)
        spec = load_prompt_spec(PROMPT_FILE)
        repair_spec = load_prompt_spec(REPAIR_FILE)
        model = spec.model or settings.groq_analysis_model
        client = GroqLLMClient(
            settings, budget=budget, max_concurrency=settings.llm_max_concurrency
        )

        spec_insight = load_prompt_spec(PROMPT_FILE)
        all_drafts: List[Dict[str, Any]] = []

        async def _run_all() -> None:
            for theme in themes:
                cluster = (
                    db.query(Cluster).filter(Cluster.theme_id == theme.id).first()
                )
                drafts, dropped = await _generate_for_theme(
                    client,
                    db,
                    theme,
                    cluster,
                    model,
                    spec_insight.content_hash,
                    repair_spec.body,
                    settings,
                )
                all_drafts.extend(drafts)
                stats["dropped"] += dropped

        asyncio.run(_run_all())

        prompt_version = spec.version_tag
        model_version = model

        for draft in all_drafts:
            cited = draft["example_review_ids"]
            conf = compute_confidence(
                db,
                cited,
                draft["frequency"],
                coherence_score=draft.get("coherence"),
            )
            score = conf["total"]
            rscore = rank_score(score, draft["business_impact"])
            agreement, notes = triangulation_label(db, cited)

            insight = Insight(
                problem=draft["problem"],
                evidence=draft["evidence"],
                frequency=draft["frequency"],
                example_review_ids=cited,
                customer_segment=draft["customer_segment"],
                business_impact=draft["business_impact"],
                opportunity=draft["opportunity"],
                confidence_score=score,
                confidence_breakdown=conf,
                rank_score=rscore,
                theme_id=draft["theme_id"],
                validation_status=agreement,
                model_version=model_version,
                prompt_version=prompt_version,
            )
            db.add(insight)
            db.flush()

            db.add(
                Validation(
                    insight_id=insight.id,
                    source_type="cross_source",
                    agreement=agreement,
                    notes=notes,
                )
            )
            stats["created"] += 1

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
