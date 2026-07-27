"""Play Store review collector."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from google_play_scraper import Sort, reviews

from app.collectors.base import BaseCollector, RawReview


class PlayStoreCollector(BaseCollector):
    source_type = "play_store"

    def fetch(self, config: Dict[str, Any]) -> List[RawReview]:
        app_id = config["app_id"]
        lang = config.get("lang", "en")
        country = config.get("country", "in")
        max_reviews = int(config.get("max_reviews", 1000))
        sort = Sort.NEWEST

        collected: List[RawReview] = []
        token = None

        while len(collected) < max_reviews:
            batch_size = min(200, max_reviews - len(collected))
            batch, token = reviews(
                app_id,
                lang=lang,
                country=country,
                sort=sort,
                count=batch_size,
                continuation_token=token,
            )
            if not batch:
                break
            for item in batch:
                text = (item.get("content") or "").strip()
                if not text:
                    continue
                posted = item.get("at")
                if posted and posted.tzinfo is None:
                    posted = posted.replace(tzinfo=timezone.utc)
                collected.append(
                    RawReview(
                        text=text,
                        external_id=str(item.get("reviewId") or ""),
                        rating=float(item["score"]) if item.get("score") is not None else None,
                        posted_at=posted,
                        author_hash=str(item.get("userName") or "")[:128] or None,
                        raw_payload=dict(item),
                    )
                )
            if token is None:
                break

        return collected[:max_reviews]
