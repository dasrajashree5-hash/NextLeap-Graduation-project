"""JSON review collector."""

import json
from typing import Any, Dict, List, Optional, Tuple

from app.collectors.base import RawReview
from app.core.errors import ValidationError


class JsonReviewCollector:
    source_type = "json"

    def parse(
        self,
        file_bytes: bytes,
        column_map: Optional[Dict[str, str]] = None,
    ) -> Tuple[List[RawReview], List[Dict[str, Any]]]:
        column_map = column_map or {}
        try:
            payload = json.loads(file_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValidationError("Invalid JSON file", details=[{"row": 0, "error": str(exc)}])

        if isinstance(payload, dict):
            items = payload.get("reviews") or payload.get("data") or payload.get("items")
            if items is None:
                raise ValidationError(
                    "JSON object must contain reviews, data, or items array",
                    details=[],
                )
        elif isinstance(payload, list):
            items = payload
        else:
            raise ValidationError("JSON root must be an array or object", details=[])

        text_keys = [column_map.get("text", "text"), "review", "body", "content"]
        reviews: List[RawReview] = []
        errors: List[Dict[str, Any]] = []

        for idx, item in enumerate(items, start=1):
            if not isinstance(item, dict):
                errors.append({"row": idx, "error": "entry is not an object"})
                continue
            text = _first_str(item, text_keys)
            if not text:
                errors.append({"row": idx, "error": "empty text"})
                continue
            rating = item.get(column_map.get("rating", "rating") or "rating")
            try:
                rating_f = float(rating) if rating is not None and rating != "" else None
            except (TypeError, ValueError):
                errors.append({"row": idx, "error": f"invalid rating: {rating}"})
                continue
            ext = _first_str(item, [column_map.get("external_id", "external_id"), "id", "review_id"])
            author = _first_str(item, [column_map.get("author", "author"), "user", "username"])
            reviews.append(
                RawReview(
                    text=text,
                    external_id=ext,
                    rating=rating_f,
                    posted_at=None,
                    author_hash=author[:128] if author else None,
                    raw_payload=item,
                )
            )

        if errors and not reviews:
            raise ValidationError("JSON validation failed", details=errors)

        return reviews, errors


def _first_str(item: Dict[str, Any], keys: List[str]) -> str:
    for key in keys:
        if not key:
            continue
        val = item.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""
