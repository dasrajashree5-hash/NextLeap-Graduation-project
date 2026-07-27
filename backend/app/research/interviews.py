"""Interview upload and persistence."""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models import Interview


def create_interview(
    db: Session,
    *,
    transcript: str,
    participant_segment: Optional[str] = None,
    notes: Optional[str] = None,
    conducted_at: Optional[datetime] = None,
) -> Interview:
    row = Interview(
        participant_segment=participant_segment,
        transcript=transcript.strip(),
        notes=notes,
        conducted_at=conducted_at,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def parse_interview_csv(content: bytes) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """CSV columns: participant_segment, transcript, notes, conducted_at (optional)."""
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    rows: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    for i, raw in enumerate(reader, start=2):
        transcript = (raw.get("transcript") or raw.get("Transcript") or "").strip()
        if not transcript:
            errors.append({"row": i, "error": "transcript is required"})
            continue
        segment = raw.get("participant_segment") or raw.get("segment")
        notes = raw.get("notes")
        conducted = raw.get("conducted_at")
        conducted_at = None
        if conducted:
            try:
                conducted_at = datetime.fromisoformat(conducted.replace("Z", "+00:00"))
            except ValueError:
                errors.append({"row": i, "error": f"invalid conducted_at: {conducted}"})
                continue
        rows.append(
            {
                "participant_segment": segment,
                "transcript": transcript,
                "notes": notes,
                "conducted_at": conducted_at,
            }
        )
    return rows, errors


def parse_interview_upload(
    content: bytes,
    filename: str,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    lower = filename.lower()
    if lower.endswith(".csv"):
        return parse_interview_csv(content)
    if lower.endswith(".json"):
        data = json.loads(content.decode("utf-8"))
        if isinstance(data, dict):
            data = data.get("interviews", [data])
        if not isinstance(data, list):
            return [], [{"error": "JSON must be a list or {interviews: [...]}"}]
        out: List[Dict[str, Any]] = []
        for i, item in enumerate(data, start=1):
            transcript = (item.get("transcript") or "").strip()
            if not transcript:
                return [], [{"row": i, "error": "transcript required"}]
            out.append(item)
        return out, []
    # Plain text file — single interview
    transcript = content.decode("utf-8").strip()
    if len(transcript) < 20:
        return [], [{"error": "transcript too short"}]
    return [{"transcript": transcript, "participant_segment": None}], []


def bulk_create_interviews(db: Session, items: List[Dict[str, Any]]) -> int:
    count = 0
    for item in items:
        create_interview(
            db,
            transcript=item["transcript"],
            participant_segment=item.get("participant_segment"),
            notes=item.get("notes"),
            conducted_at=item.get("conducted_at"),
        )
        count += 1
    return count
