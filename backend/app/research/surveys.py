"""Survey CSV ingestion and aggregation."""

from __future__ import annotations

import csv
import io
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models import Survey

_PSEUDONYM_MAP: Dict[str, str] = {}
_PSEUDONYM_COUNTER = 0

QUESTION_COLUMNS = {
    "order_frequency": "Q1 order frequency",
    "categories_purchased": "Q2 categories purchased",
    "shopping_mode": "Q3 shopping mode",
    "pct_repeat_purchase": "Q4 repeat purchase share",
    "new_product_discovery_frequency": "Q5 new product discovery",
    "reasons_not_buying_new": "Q6 barriers to new products",
    "encouragers_to_try_new": "Q7 encouragers",
    "bought_due_to_recommendation": "Q8 bought via recommendation",
    "ai_assistant_interest": "Q9 AI assistant interest",
    "useful_ai_recommendations": "Q10 useful AI rec types",
    "ai_trust_score": "Q11 AI trust score",
    "trust_builders": "Q12 trust builders",
    "biggest_frustration": "Q13 biggest frustration",
    "one_improvement": "Q14 one improvement",
    "additional_suggestions": "Q15 additional suggestions",
}


def _pseudonym(name: str) -> str:
    global _PSEUDONYM_COUNTER  # noqa: PLW0603
    cleaned = (name or "").strip()
    if not cleaned:
        return "anonymous"
    if cleaned not in _PSEUDONYM_MAP:
        _PSEUDONYM_COUNTER += 1
        _PSEUDONYM_MAP[cleaned] = f"R{_PSEUDONYM_COUNTER:02d}"
    return _PSEUDONYM_MAP[cleaned]


def _segment(row: Dict[str, str]) -> str:
    age = (row.get("age_group") or "").strip()
    occ = (row.get("occupation") or "").strip()
    parts = [p for p in (age, occ) if p]
    return " · ".join(parts) if parts else "unknown"


def _parse_timestamp(raw: str) -> Optional[datetime]:
    raw = (raw or "").strip()
    if not raw:
        return None
    for fmt in ("%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def _split_multi(value: str) -> List[str]:
    if not value or not value.strip():
        return []
    parts = re.split(r",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", value)
    return [p.strip().strip('"') for p in parts if p.strip()]


def ingest_survey_csv(db: Session, content: bytes, *, replace: bool = True) -> Dict[str, Any]:
    if replace:
        db.query(Survey).delete()
        db.flush()

    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    rows_loaded = 0
    respondents = set()

    for raw in reader:
        name = raw.get("name") or ""
        respondent_id = _pseudonym(name)
        respondents.add(respondent_id)
        segment = _segment(raw)
        submitted_at = _parse_timestamp(raw.get("timestamp") or "")

        for col, question_label in QUESTION_COLUMNS.items():
            val = (raw.get(col) or "").strip()
            if not val:
                continue
            if col in (
                "reasons_not_buying_new",
                "encouragers_to_try_new",
                "useful_ai_recommendations",
                "trust_builders",
                "categories_purchased",
            ):
                for part in _split_multi(val):
                    db.add(
                        Survey(
                            question=f"{question_label}",
                            response=part,
                            respondent_segment=f"{respondent_id} · {segment}",
                            submitted_at=submitted_at,
                        )
                    )
                    rows_loaded += 1
            else:
                db.add(
                    Survey(
                        question=question_label,
                        response=val,
                        respondent_segment=f"{respondent_id} · {segment}",
                        submitted_at=submitted_at,
                    )
                )
                rows_loaded += 1

    db.commit()
    return {
        "rows_loaded": rows_loaded,
        "respondents": len(respondents),
    }


def load_default_survey_csv(db: Session, project_root: Path) -> Dict[str, Any]:
    path = project_root / "data" / "primary-survey-responses.csv"
    if not path.is_file():
        alt = project_root.parent / "data" / "primary-survey-responses.csv"
        path = alt if alt.is_file() else path
    content = path.read_bytes()
    return ingest_survey_csv(db, content, replace=True)


def aggregate_surveys(db: Session) -> List[Dict[str, Any]]:
    rows = db.query(Survey).all()
    counts: Dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for row in rows:
        seg = (row.respondent_segment or "unknown").split(" · ")[-1]
        counts[(row.question, row.response)][seg] += 1

    out: List[Dict[str, Any]] = []
    for (question, response), seg_counts in sorted(counts.items()):
        total = sum(seg_counts.values())
        out.append(
            {
                "question_key": question,
                "response": response,
                "count": total,
                "segments": dict(seg_counts),
            }
        )
    return out


def survey_text_corpus(db: Session) -> List[str]:
    open_q = ("Q13", "Q14", "Q15")
    texts: List[str] = []
    for row in db.query(Survey).all():
        if any(row.question.startswith(prefix) for prefix in open_q):
            if row.response.strip():
                texts.append(row.response.strip())
    return texts
