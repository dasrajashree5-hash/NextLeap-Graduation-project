"""Map human research findings to Phase 4 theme taxonomy."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.models import Interview, Survey
from app.schemas.analysis import THEME_CATEGORIES
from app.research.surveys import survey_text_corpus


def build_affinity_map(db: Session) -> List[Dict[str, Any]]:
    groups: Dict[str, Dict[str, Any]] = {
        cat: {
            "theme_category": cat,
            "sources": set(),
            "finding_count": 0,
            "sample_quotes": [],
            "discovery_barriers": set(),
        }
        for cat in THEME_CATEGORIES
    }

    interviews = db.query(Interview).all()
    for iv in interviews:
        coding = iv.coding_json or {}
        for theme in coding.get("theme_categories") or []:
            if theme not in groups:
                continue
            groups[theme]["sources"].add(f"interview:{iv.id}")
            groups[theme]["finding_count"] += 1
        for barrier in coding.get("discovery_barriers") or []:
            for theme in coding.get("theme_categories") or ["Category Discovery"]:
                if theme in groups:
                    groups[theme]["discovery_barriers"].add(barrier)
        for quote in coding.get("quotes") or []:
            theme = quote.get("theme_category")
            if theme in groups and len(groups[theme]["sample_quotes"]) < 4:
                groups[theme]["sample_quotes"].append(quote.get("quote", ""))

        if iv.pain_points and not coding:
            groups["Shopping Habit"]["finding_count"] += 1
            groups["Shopping Habit"]["sources"].add(f"interview:{iv.id}")

    # Survey closed-ended themes
    survey_rows = db.query(Survey).all()
    for row in survey_rows:
        q = row.question
        resp = row.response
        target = None
        if q.startswith("Q6"):
            target = "Category Discovery"
        elif q.startswith("Q3"):
            target = "Shopping Habit"
        elif q.startswith("Q7") or q.startswith("Q10"):
            target = "Recommendations"
        elif q.startswith("Q11") or q.startswith("Q12") or q.startswith("Q8"):
            target = "Trust"
        elif q.startswith("Q13") or q.startswith("Q14"):
            target = "Search" if "search" in resp.lower() else "Category Discovery"
        if target and target in groups:
            groups[target]["sources"].add("survey")
            groups[target]["finding_count"] += 1

    for text in survey_text_corpus(db):
        lowered = text.lower()
        if "search" in lowered:
            groups["Search"]["finding_count"] += 1
            groups["Search"]["sources"].add("survey")
            if len(groups["Search"]["sample_quotes"]) < 4:
                groups["Search"]["sample_quotes"].append(text[:200])
        if "recommend" in lowered or "trust" in lowered:
            groups["Trust"]["finding_count"] += 1
            groups["Trust"]["sources"].add("survey")
        if "discount" in lowered or "price" in lowered:
            groups["Price"]["finding_count"] += 1
            groups["Price"]["sources"].add("survey")

    out: List[Dict[str, Any]] = []
    for cat in THEME_CATEGORIES:
        g = groups[cat]
        if g["finding_count"] == 0:
            continue
        out.append(
            {
                "theme_category": cat,
                "sources": sorted(g["sources"]),
                "finding_count": g["finding_count"],
                "sample_quotes": [q for q in g["sample_quotes"] if q],
                "discovery_barriers": sorted(g["discovery_barriers"]),
            }
        )
    out.sort(key=lambda x: x["finding_count"], reverse=True)
    return out
