"""Load sample interviews and survey for offline demo."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.models import Interview
from app.research.coding import CODING_VERSION, code_interview
from app.research.interviews import bulk_create_interviews
from app.research.surveys import ingest_survey_csv


def _sample_interviews() -> list[Dict[str, Any]]:
    return [
        {
            "participant_segment": "Metro salaried · 25-34 · Mumbai",
            "conducted_at": datetime(2026, 7, 22, tzinfo=timezone.utc),
            "transcript": (
                "Interviewer: Walk me through your last Blinkit order. "
                "Participant: Same as always — snacks, detergent, milk. I literally search "
                "'Amul milk' and checkout in under two minutes. I never browse categories because "
                "it feels like wasting time. Once I tried to find face wash and search showed "
                "weird unrelated items, so I gave up and bought it offline. "
                "If something new appears, I need reviews visible before I trust it."
            ),
        },
        {
            "participant_segment": "Parent · 30-34 · Bengaluru",
            "conducted_at": datetime(2026, 7, 23, tzinfo=timezone.utc),
            "transcript": (
                "Participant: Groceries on Blinkit every week, but baby wipes and diapers I still "
                "order from another app because I don't know if Blinkit carries my brand. "
                "I didn't know there was a baby section until my friend mentioned it. "
                "Trust is the issue — if I'm trying a new category for my kid, I need ratings "
                "and easy returns spelled out."
            ),
        },
        {
            "participant_segment": "Pet owner · 28 · Guwahati",
            "conducted_at": datetime(2026, 7, 23, tzinfo=timezone.utc),
            "transcript": (
                "Participant: Blinkit is perfect for late-night snacks. For pet food I never think "
                "of Blinkit — habit keeps me on a pet store site. If checkout suggested one small "
                "pet treat based on what I already buy, I might say yes, but only with a clear "
                "reason and discount. Price on specialty items feels higher than the market."
            ),
        },
        {
            "participant_segment": "Student · 18-24 · Meerut",
            "conducted_at": datetime(2026, 7, 24, tzinfo=timezone.utc),
            "transcript": (
                "Participant: I open Blinkit when hostel snacks run out. Discovery happens only "
                "when friends share a deal link. Personalized recommendations feel random; I dismiss "
                "them. Discounts are the only thing that makes me try something new. "
                "I'm not interested in an AI assistant — just show me cheaper alternatives."
            ),
        },
        {
            "participant_segment": "Daily user · skeptical · Kolkata",
            "conducted_at": datetime(2026, 7, 25, tzinfo=timezone.utc),
            "transcript": (
                "Participant: I order daily but it's the same basket. Blinkit keeps pushing "
                "electronics and I ignore it. An AI shopping assistant sounds gimmicky; I don't trust "
                "AI recommendations more than my own list. Put one relevant suggestion in the cart "
                "with customer reviews and I'll look — homepage banners I never see."
            ),
        },
    ]


def seed_research(db: Session, project_root: Path, *, code: bool = True) -> Dict[str, Any]:
    existing = db.query(Interview).count()
    interviews_loaded = 0
    if existing == 0:
        interviews_loaded = bulk_create_interviews(db, _sample_interviews())
    else:
        interviews_loaded = existing

    survey_path = project_root / "data" / "primary-survey-responses.csv"
    if not survey_path.is_file():
        survey_path = project_root.parent / "data" / "primary-survey-responses.csv"
    survey_stats = {"rows_loaded": 0, "respondents": 0}
    if survey_path.is_file():
        survey_stats = ingest_survey_csv(db, survey_path.read_bytes(), replace=True)

    coded = 0
    if code:
        for row in db.query(Interview).filter(Interview.coding_json.is_(None)).all():
            code_interview(db, row, use_llm=False)
            coded += 1
        for row in db.query(Interview).filter(Interview.coding_version != CODING_VERSION).all():
            code_interview(db, row, use_llm=False)
            coded += 1

    return {
        "interviews_loaded": interviews_loaded,
        "survey_rows_loaded": survey_stats.get("rows_loaded", 0),
        "interviews_coded": coded,
    }


def load_seed_file(db: Session, path: Path) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data if isinstance(data, list) else data.get("interviews", [])
    return bulk_create_interviews(db, items)
