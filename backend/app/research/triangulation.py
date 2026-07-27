"""Compare AI insights against interview and survey evidence."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models import Insight, Interview, Survey, Theme, Validation
from app.research.affinity import build_affinity_map
from app.research.surveys import aggregate_surveys


def _theme_for_insight(db: Session, insight: Insight) -> Optional[str]:
    if insight.theme_id:
        theme = db.query(Theme).filter(Theme.id == insight.theme_id).first()
        if theme and theme.category:
            return theme.category
    problem = (insight.problem or "").lower()
    for cat in (
        "Category Discovery",
        "Shopping Habit",
        "Recommendations",
        "Trust",
        "Search",
        "Price",
        "Delivery",
    ):
        if cat.lower() in problem:
            return cat
    return None


def _interview_support(
    db: Session,
    theme_category: Optional[str],
    problem_text: str,
) -> Tuple[List[int], str, float]:
    """Returns interview ids, evidence snippet, support score 0-1."""
    interviews = db.query(Interview).all()
    matched_ids: List[int] = []
    evidence_parts: List[str] = []
    problem_lower = problem_text.lower()

    for iv in interviews:
        coding = iv.coding_json or {}
        themes = coding.get("theme_categories") or []
        score = 0.0
        if theme_category and theme_category in themes:
            score += 0.5
        pain = (iv.pain_points or "").lower()
        if any(tok in pain for tok in problem_lower.split() if len(tok) > 4):
            score += 0.2
        matched_this = False
        for quote in coding.get("quotes") or []:
            qtext = (quote.get("quote") or "").lower()
            if theme_category and quote.get("theme_category") == theme_category:
                score += 0.3
                evidence_parts.append(f'Interview {iv.id}: "{quote.get("quote", "")[:120]}"')
                matched_ids.append(iv.id)
                matched_this = True
                break
            if any(w in qtext for w in ("recommend", "trust", "search", "habit", "discover")):
                if any(w in problem_lower for w in ("recommend", "trust", "search", "habit", "discover")):
                    score += 0.25
                    evidence_parts.append(f'Interview {iv.id}: "{quote.get("quote", "")[:120]}"')
                    matched_ids.append(iv.id)
                    matched_this = True
                    break
        if not matched_this and score >= 0.5:
            matched_ids.append(iv.id)

    support = min(1.0, len(matched_ids) / max(len(interviews), 1)) if matched_ids else 0.0
    return matched_ids, "; ".join(evidence_parts[:3]), support


def _survey_support(db: Session, theme_category: Optional[str]) -> Tuple[int, str]:
    aggregates = aggregate_surveys(db)
    count = 0
    notes: List[str] = []
    theme_prefix = {
        "Category Discovery": "Q6",
        "Shopping Habit": "Q3",
        "Recommendations": "Q7",
        "Trust": "Q11",
        "Search": "Q13",
        "Price": "Q7",
    }
    prefix = theme_prefix.get(theme_category or "", "")
    for item in aggregates:
        if prefix and item["question_key"].startswith(prefix):
            count += item["count"]
            notes.append(f'{item["response"]} (n={item["count"]})')
    return count, "; ".join(notes[:4])


def _classify_status(
    interview_support: float,
    survey_count: int,
    insight: Insight,
    contradict: bool,
) -> str:
    if contradict:
        return "rejected"
    if interview_support >= 0.55 and survey_count >= 2:
        return "validated"
    if interview_support >= 0.35 or survey_count >= 1:
        return "partially_supported"
    return "partially_supported"


def _detect_contradiction(insight: Insight, interviews: List[Interview]) -> bool:
    """Flag insights claiming universal AI demand when interviews express skepticism."""
    problem = (insight.problem + " " + (insight.evidence or "")).lower()
    ai_hype = any(
        phrase in problem
        for phrase in (
            "users want ai",
            "universal appetite for ai",
            "everyone wants recommendations",
            "high demand for ai assistant",
        )
    )
    if not ai_hype and "recommendation" not in problem:
        # Specific rejection case: insight says users crave AI; interviews skeptical
        if "ai" in problem and "recommend" in problem and "trust" not in problem:
            ai_hype = True

    skeptic_quotes = 0
    for iv in interviews:
        text = (iv.transcript or "").lower()
        if re.search(r"\b(not interested|skeptic|don't trust ai|dismiss)\b", text):
            skeptic_quotes += 1
        coding = iv.coding_json or {}
        if "trust" in coding.get("discovery_barriers", []):
            if "recommend" in problem or "ai" in problem:
                skeptic_quotes += 1

    if ai_hype and skeptic_quotes >= 2:
        return True

    # Insight: delivery is primary discovery blocker — interviews emphasize habit/search
    if "delivery" in problem and "discovery" in problem:
        habit_focus = sum(
            1
            for iv in interviews
            if "Shopping Habit" in (iv.coding_json or {}).get("theme_categories", [])
            or "habit" in (iv.discovery_barriers or "")
        )
        if habit_focus >= 2:
            return True
    return False


def triangulate_insights(db: Session) -> Dict[str, Any]:
    affinity = {a["theme_category"]: a for a in build_affinity_map(db)}
    insights = db.query(Insight).all()
    stats = {"validated": 0, "rejected": 0, "partially_supported": 0, "new_discovery": 0}

    db.query(Validation).filter(Validation.source_type.in_(["interview", "survey", "triangulation"])).delete()
    db.flush()

    interviews = db.query(Interview).all()
    matched_themes = set()

    for insight in insights:
        theme_cat = _theme_for_insight(db, insight)
        if theme_cat:
            matched_themes.add(theme_cat)
        iv_ids, iv_evidence, iv_score = _interview_support(
            db, theme_cat, insight.problem or ""
        )
        survey_count, survey_evidence = _survey_support(db, theme_cat)
        contradict = _detect_contradiction(insight, interviews)
        status = _classify_status(iv_score, survey_count, insight, contradict)

        human_evidence = " | ".join(
            part for part in (iv_evidence, survey_evidence) if part
        )
        insight.validation_status = status
        db.add(insight)

        db.add(
            Validation(
                insight_id=insight.id,
                source_type="triangulation",
                agreement=status,
                notes=human_evidence or "No direct human citation; theme overlap weak.",
            )
        )
        if iv_ids:
            db.add(
                Validation(
                    insight_id=insight.id,
                    source_type="interview",
                    agreement=status,
                    notes=iv_evidence,
                )
            )
        if survey_count:
            db.add(
                Validation(
                    insight_id=insight.id,
                    source_type="survey",
                    agreement=status,
                    notes=survey_evidence,
                )
            )
        stats[status] = stats.get(status, 0) + 1

    # Human-only themes -> new_discovery placeholder on highest affinity gap
    for cat, group in affinity.items():
        if cat in matched_themes:
            continue
        if group["finding_count"] < 2:
            continue
        stats["new_discovery"] += 1

    db.commit()
    return {"stats": stats, "affinity_groups": len(affinity)}


def run_triangulation(db: Session) -> Dict[str, Any]:
    run_stats = triangulate_insights(db)
    return run_stats
