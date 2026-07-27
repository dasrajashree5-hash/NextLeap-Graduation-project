"""App Store review collector (public RSS JSON)."""

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from xml.etree import ElementTree

import httpx

from app.collectors.base import BaseCollector, RawReview

ITUNES_NS = {
    "im": "http://itunes.apple.com/rss",
    "atom": "http://www.w3.org/2005/Atom",
}


class AppStoreCollector(BaseCollector):
    source_type = "app_store"

    def fetch(self, config: Dict[str, Any]) -> List[RawReview]:
        app_id = str(config["app_id"])
        country = config.get("country", "in")
        max_reviews = int(config.get("max_reviews", 1000))

        collected: List[RawReview] = []
        page = 1

        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            while len(collected) < max_reviews:
                url = (
                    f"https://itunes.apple.com/{country}/rss/customerreviews/"
                    f"page={page}/id={app_id}/sortby=mostrecent/json"
                )
                response = client.get(url)
                if response.status_code != 200:
                    break
                data = response.json()
                entries = data.get("feed", {}).get("entry") or []
                if not entries:
                    break
                if page == 1 and len(entries) == 1:
                    # Sometimes only app metadata entry
                    break

                for entry in entries:
                    if not isinstance(entry, dict):
                        continue
                    if "im:rating" not in entry and "content" not in entry:
                        continue
                    text = _entry_text(entry)
                    if not text:
                        continue
                    rating_raw = _nested(entry, "im:rating", "label")
                    rating = float(rating_raw) if rating_raw else None
                    title = _nested(entry, "title", "label") or ""
                    author = _nested(entry, "author", "name", "label") or ""
                    external = _nested(entry, "id", "label") or hashlib.sha256(
                        (title + text).encode()
                    ).hexdigest()[:32]
                    updated = _nested(entry, "updated", "label")
                    posted = _parse_iso(updated)
                    collected.append(
                        RawReview(
                            text=text,
                            external_id=str(external),
                            rating=rating,
                            posted_at=posted,
                            author_hash=author[:128] if author else None,
                            raw_payload=entry,
                        )
                    )
                    if len(collected) >= max_reviews:
                        break

                page += 1
                if page > 50:
                    break

        return collected[:max_reviews]


def _nested(entry: Dict[str, Any], *keys: str) -> Optional[str]:
    cur: Any = entry
    for key in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    if isinstance(cur, dict) and "label" in cur:
        return str(cur["label"])
    if isinstance(cur, str):
        return cur
    return None


def _entry_text(entry: Dict[str, Any]) -> str:
    content = entry.get("content")
    if isinstance(content, dict):
        label = content.get("label")
        if isinstance(label, str):
            return _strip_html(label).strip()
    title = _nested(entry, "title", "label")
    if title and title != "Blinkit: Groceries & More":
        return title.strip()
    return ""


def _strip_html(text: str) -> str:
    try:
        root = ElementTree.fromstring(f"<root>{text}</root>")
        return "".join(root.itertext())
    except ElementTree.ParseError:
        return text


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None
