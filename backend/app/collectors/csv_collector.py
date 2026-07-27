"""CSV review collector."""

import csv
import io
from typing import Any, Dict, List, Optional, Tuple

from app.collectors.base import RawReview
from app.core.errors import ValidationError


TEXT_COLUMNS = ("text", "review", "body", "content", "review_text")
OPTIONAL_COLUMNS = ("external_id", "rating", "posted_at", "author", "author_hash")


class CsvReviewCollector:
    source_type = "csv"

    def parse(
        self,
        file_bytes: bytes,
        encoding: str = "utf-8",
        column_map: Optional[Dict[str, str]] = None,
    ) -> Tuple[List[RawReview], List[Dict[str, Any]]]:
        """Returns (reviews, row_errors). Raises ValidationError if header invalid."""
        column_map = column_map or {}
        try:
            text = file_bytes.decode(encoding)
        except UnicodeDecodeError as exc:
            raise ValidationError("File is not valid UTF-8", details=[{"row": 0, "error": str(exc)}])

        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames:
            raise ValidationError("CSV has no header row", details=[])

        fields = [f.strip() for f in reader.fieldnames if f]
        text_col = _resolve_column(fields, column_map, "text", TEXT_COLUMNS)
        if not text_col:
            raise ValidationError(
                "CSV must include a text column (text, review, body, or content)",
                details=[{"row": 0, "error": f"headers={fields}"}],
            )

        ext_col = _resolve_column(fields, column_map, "external_id", ("external_id", "id", "review_id"))
        rating_col = _resolve_column(fields, column_map, "rating", ("rating", "score", "stars"))
        date_col = _resolve_column(fields, column_map, "posted_at", ("posted_at", "date", "timestamp"))
        author_col = _resolve_column(fields, column_map, "author", ("author", "user", "username"))

        reviews: List[RawReview] = []
        errors: List[Dict[str, Any]] = []

        for idx, row in enumerate(reader, start=2):
            raw_text = (row.get(text_col) or "").strip()
            if not raw_text:
                errors.append({"row": idx, "error": "empty text"})
                continue
            rating = None
            if rating_col and row.get(rating_col):
                try:
                    rating = float(row[rating_col])
                except ValueError:
                    errors.append({"row": idx, "error": f"invalid rating: {row[rating_col]}"})
                    continue
            reviews.append(
                RawReview(
                    text=raw_text,
                    external_id=(row.get(ext_col) or "").strip() or None if ext_col else None,
                    rating=rating,
                    posted_at=None,
                    author_hash=(row.get(author_col) or "").strip()[:128] or None if author_col else None,
                    raw_payload=dict(row),
                )
            )

        if errors and not reviews:
            raise ValidationError("CSV validation failed", details=errors)

        return reviews, errors


def _resolve_column(
    headers: List[str],
    column_map: Dict[str, str],
    logical: str,
    candidates: Tuple[str, ...],
) -> Optional[str]:
    if logical in column_map and column_map[logical] in headers:
        return column_map[logical]
    lower = {h.lower(): h for h in headers}
    for cand in candidates:
        if cand in headers:
            return cand
        if cand.lower() in lower:
            return lower[cand.lower()]
    return None
