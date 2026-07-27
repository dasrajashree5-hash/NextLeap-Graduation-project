"""Rank validated problems by reach, severity, north-star impact, and effort."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models import Insight, Interview, Opportunity, Run, Survey
from app.research.affinity import build_affinity_map
from app.research.surveys import aggregate_surveys


def _clamp_score(value: float) -> float:
    return max(1.0, min(5.0, round(value, 2)))


def _reach_score(db: Session, insight: Insight) -> float:
    freq = insight.frequency or 1
    interview_n = db.query(Interview).count()
    survey_rows = db.query(Survey).count()
    base = 1.0 + min(4.0, (freq / 50) * 4)
    if interview_n >= 5:
        base += 0.5
    if survey_rows >= 50:
        base += 0.5
    return _clamp_score(base)


def _severity_score(insight: Insight) -> float:
    text = (insight.problem or "") + " " + (insight.evidence or "")
    lowered = text.lower()
    if any(w in lowered for w in ("never", "blocked", "cannot", "fail", "frustrated")):
        return 4.5
    if any(w in lowered for w in ("hard", "difficult", "barrier", "trust")):
        return 3.5
    return 2.5


def _north_star_score(insight: Insight) -> float:
    text = (insight.problem + " " + (insight.business_impact or "")).lower()
    if any(
        w in text
        for w in ("category discovery", "basket expansion", "cross-category", "adjacent")
    ):
        return 5.0
    if "recommend" in text or "discover" in text:
        return 4.0
    return 2.0


def _effort_score(insight: Insight) -> float:
    opp = (insight.opportunity or "").lower()
    if any(w in opp for w in ("copy change", "banner", "tooltip", "sort order")):
        return 2.0
    if any(w in opp for w in ("model", "retrain", "new pipeline", "warehouse")):
        return 4.5
    return 3.0


def _total(reach: float, severity: float, north: float, effort: float) -> float:
    # Lower effort is better — invert onto 1-5 scale contribution
    effort_component = 6.0 - effort
    return round(
        0.25 * reach + 0.25 * severity + 0.35 * north + 0.15 * effort_component,
        3,
    )


def run_opportunity_assessment(db: Session, *, replace: bool = True) -> Dict[str, Any]:
    run = Run(phase="opportunities", status="running")
    db.add(run)
    db.commit()
    db.refresh(run)

    if replace:
        db.query(Opportunity).delete()
        db.flush()

    insights = (
        db.query(Insight)
        .filter(Insight.validation_status.in_(["validated", "partially_supported", "new_discovery"]))
        .all()
    )
    if not insights:
        insights = db.query(Insight).order_by(Insight.rank_score.desc()).limit(10).all()

    scored: List[Dict[str, Any]] = []
    for insight in insights:
        reach = _reach_score(db, insight)
        severity = _severity_score(insight)
        north = _north_star_score(insight)
        effort = _effort_score(insight)
        total = _total(reach, severity, north, effort)
        rationale = {
            "reach": {"score": reach, "drivers": ["review_frequency", "survey_n", "interview_n"]},
            "severity": {"score": severity, "drivers": ["problem_language"]},
            "north_star": {"score": north, "drivers": ["category_expansion_keywords"]},
            "effort": {"score": effort, "drivers": ["opportunity_implementation_hints"]},
            "weights": {"reach": 0.25, "severity": 0.25, "north_star": 0.35, "effort": 0.15},
        }
        scored.append(
            {
                "insight": insight,
                "reach": reach,
                "severity": severity,
                "north": north,
                "effort": effort,
                "total": total,
                "rationale": rationale,
            }
        )

    # Boost human-only affinity themes not covered by insights
    affinity = build_affinity_map(db)
    aggregates = aggregate_surveys(db)
    for group in affinity[:3]:
        if any(group["theme_category"] in (s["insight"].problem or "") for s in scored):
            continue
        reach = _clamp_score(2.0 + min(2.0, group["finding_count"] / 5))
        severity = 3.5
        north = 4.5 if group["theme_category"] == "Category Discovery" else 3.5
        effort = 3.0
        total = _total(reach, severity, north, effort)
        pseudo = Insight(
            problem=f"Human research theme: {group['theme_category']}",
            evidence="; ".join(group.get("sample_quotes") or [])[:500],
            frequency=group["finding_count"],
            validation_status="new_discovery",
        )
        scored.append(
            {
                "insight": pseudo,
                "reach": reach,
                "severity": severity,
                "north": north,
                "effort": effort,
                "total": total,
                "rationale": {
                    "reach": {"score": reach, "drivers": ["affinity_finding_count"]},
                    "severity": {"score": severity, "drivers": ["qualitative_pain"]},
                    "north_star": {"score": north, "drivers": ["theme_category"]},
                    "effort": {"score": effort, "drivers": ["default"]},
                    "survey_hint": aggregates[:2],
                },
                "insight_id": None,
            }
        )

    scored.sort(key=lambda x: x["total"], reverse=True)
    created = 0
    for rank, item in enumerate(scored[:10], start=1):
        insight = item["insight"]
        insight_id = insight.id if getattr(insight, "id", None) else None
        row = Opportunity(
            insight_id=insight_id,
            title=(insight.problem or "")[:512],
            reach_score=item["reach"],
            severity_score=item["severity"],
            north_star_score=item["north"],
            effort_score=item["effort"],
            total_score=item["total"],
            scoring_rationale=item["rationale"],
            rank=rank,
        )
        db.add(row)
        created += 1

    run.status = "completed"
    run.stats_json = {"created": created}
    run.finished_at = datetime.now(timezone.utc)
    db.commit()
    return {"run_id": run.id, "stats": {"created": created}}


def list_opportunities(db: Session, limit: int = 10) -> List[Opportunity]:
    return (
        db.query(Opportunity)
        .order_by(Opportunity.rank.asc())
        .limit(limit)
        .all()
    )
