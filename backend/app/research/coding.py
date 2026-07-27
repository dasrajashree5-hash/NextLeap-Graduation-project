"""LLM-assisted and heuristic interview coding."""

from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.llm.groq_client import GroqClient, GroqLLMClient
from app.llm.json_utils import validate_with_repair
from app.llm.prompts import load_prompt_spec, render_prompt
from app.models import Interview, Run
from app.schemas.analysis import THEME_CATEGORIES
from app.schemas.research import CodedQuote, InterviewCodingOutput

logger = logging.getLogger(__name__)

PROMPT_FILE = "interview_coding.v1.txt"
REPAIR_FILE = "json_repair.v1.txt"
CODING_VERSION = "1.0.0"

_BARRIER_KEYWORDS = {
    "awareness": re.compile(r"\b(didn't know|never knew|unaware|discover|find out)\b", re.I),
    "trust": re.compile(r"\b(trust|skeptic|review|rating|return|refund)\b", re.I),
    "price": re.compile(r"\b(expensive|overpriced|cheaper|discount|price)\b", re.I),
    "search": re.compile(r"\b(search|find|filter|couldn't locate)\b", re.I),
    "quality_doubt": re.compile(r"\b(quality|fresh|expiry|fake)\b", re.I),
    "habit": re.compile(r"\b(habit|same order|repeat|routine|already know)\b", re.I),
}

_THEME_KEYWORDS = {
    "Category Discovery": re.compile(r"\b(new categor|expand|pet|baby|beauty|electronics)\b", re.I),
    "Shopping Habit": re.compile(r"\b(habit|repeat|routine|same basket)\b", re.I),
    "Price": re.compile(r"\b(price|expensive|discount|deal)\b", re.I),
    "Search": re.compile(r"\b(search|find|browse)\b", re.I),
    "Recommendations": re.compile(r"\b(recommend|suggest|personaliz)\b", re.I),
    "Trust": re.compile(r"\b(trust|review|rating|return)\b", re.I),
    "Delivery": re.compile(r"\b(deliver|late|rider)\b", re.I),
    "Availability": re.compile(r"\b(out of stock|unavailable|small town)\b", re.I),
}


def _find_quote_span(transcript: str, quote: str) -> Tuple[int, int]:
    idx = transcript.find(quote)
    if idx >= 0:
        return idx, idx + len(quote)
    lowered = transcript.lower()
    q = quote.lower()
    idx = lowered.find(q)
    if idx >= 0:
        return idx, idx + len(quote)
    return 0, min(len(transcript), max(len(quote), 40))


def _heuristic_code(interview: Interview) -> InterviewCodingOutput:
    text = interview.transcript or ""
    barriers = [b for b, pat in _BARRIER_KEYWORDS.items() if pat.search(text)]
    themes = [t for t, pat in _THEME_KEYWORDS.items() if pat.search(text)]
    if "Category Discovery" not in themes and re.search(r"\bpet|baby|new categor", text, re.I):
        themes.append("Category Discovery")
    themes = [t for t in themes if t in THEME_CATEGORIES]

    sentences = re.split(r"(?<=[.!?])\s+", text)
    quotes = []
    for sent in sentences:
        if len(sent) < 25:
            continue
        theme = themes[0] if themes else "Shopping Habit"
        for t in themes:
            if _THEME_KEYWORDS.get(t) and _THEME_KEYWORDS[t].search(sent):
                theme = t
                break
        start, end = _find_quote_span(text, sent[:120])
        quotes.append(
            CodedQuote(
                quote=sent[:200],
                transcript_start=start,
                transcript_end=end,
                theme_category=theme,
            )
        )
        if len(quotes) >= 5:
            break

    pain_points = []
    for pat_name, pat in _BARRIER_KEYWORDS.items():
        if pat.search(text):
            pain_points.append(f"Barrier: {pat_name}")

    jtbd = "Restock essentials quickly without spending time exploring new categories."
    if re.search(r"pet|baby", text, re.I):
        jtbd = "Buy adjacent life-stage categories (pet/baby) in the same quick trip."
    elif re.search(r"discount|student", text, re.I):
        jtbd = "Save money on staples while occasionally trying new items when discounted."

    return InterviewCodingOutput(
        pain_points=pain_points or ["Exploration friction during mission shopping"],
        jtbd=jtbd,
        discovery_barriers=barriers,
        theme_categories=themes or ["Shopping Habit"],
        quotes=quotes,
    )


def _fix_heuristic_quotes(parsed: InterviewCodingOutput, transcript: str) -> InterviewCodingOutput:
    fixed = []
    for q in parsed.quotes:
        if transcript[q.transcript_start : q.transcript_end].strip():
            fixed.append(q)
            continue
        start, end = _find_quote_span(transcript, q.quote)
        fixed.append(
            q.model_copy(update={"transcript_start": start, "transcript_end": end})
        )
    return parsed.model_copy(update={"quotes": fixed})


async def _code_one_llm(
    client: GroqLLMClient,
    interview: Interview,
    prompt_template: str,
    model: str,
    prompt_hash: str,
    repair_body: str,
    sync_client: GroqClient,
) -> InterviewCodingOutput:
    segment = interview.participant_segment or "unknown"
    prompt = render_prompt(
        prompt_template,
        segment=segment,
        transcript=interview.transcript or "",
    )

    def repair_fn(raw: str, error: str) -> str:
        repair_prompt = render_prompt(repair_body, error=error, payload=raw[:4000])
        return sync_client.complete(repair_prompt, max_tokens=1024)

    raw = await client.complete(
        prompt,
        model=model,
        max_tokens=1200,
        cache_key=f"interview-{interview.id}",
        prompt_hash=prompt_hash,
    )
    parsed, err = validate_with_repair(raw, InterviewCodingOutput, repair_fn=repair_fn)
    if parsed is None:
        raise RuntimeError(err or "coding validation failed")
    return _fix_heuristic_quotes(parsed, interview.transcript or "")


def code_interview(
    db: Session,
    interview: Interview,
    settings: Optional[Settings] = None,
    *,
    use_llm: bool = True,
) -> InterviewCodingOutput:
    settings = settings or get_settings()
    transcript = interview.transcript or ""
    if not transcript:
        raise ValueError("interview has no transcript")

    if use_llm and settings.groq_api_key:
        spec = load_prompt_spec(PROMPT_FILE)
        repair_spec = load_prompt_spec(REPAIR_FILE)
        model = spec.model or settings.groq_analysis_model
        client = GroqLLMClient(settings)
        sync_client = GroqClient(settings)
        output = asyncio.run(
            _code_one_llm(
                client,
                interview,
                spec.body,
                model,
                spec.content_hash,
                repair_spec.body,
                sync_client,
            )
        )
    else:
        output = _heuristic_code(interview)

    interview.pain_points = "; ".join(output.pain_points)
    interview.jtbd = output.jtbd
    interview.discovery_barriers = ",".join(output.discovery_barriers)
    interview.coding_json = output.model_dump()
    interview.coding_version = CODING_VERSION
    db.add(interview)
    db.commit()
    return output


def run_code_all(
    db: Session,
    settings: Optional[Settings] = None,
    *,
    use_llm: bool = True,
) -> Dict[str, Any]:
    settings = settings or get_settings()
    run = Run(phase="interview_coding", status="running")
    db.add(run)
    db.commit()
    db.refresh(run)

    stats = {"coded": 0, "failed": 0}
    try:
        rows = db.query(Interview).all()
        for row in rows:
            if row.coding_version == CODING_VERSION and row.coding_json and not use_llm:
                continue
            try:
                code_interview(db, row, settings, use_llm=use_llm)
                stats["coded"] += 1
            except Exception as exc:  # noqa: BLE001
                logger.warning("interview coding failed id=%s: %s", row.id, exc)
                stats["failed"] += 1
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
