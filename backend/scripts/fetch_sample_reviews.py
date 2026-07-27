#!/usr/bin/env python3
"""Fetch Blinkit reviews and write sample CSV for offline demos."""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.collectors.app_store import AppStoreCollector
from app.collectors.play_store import PlayStoreCollector

OUT = ROOT / "data" / "sample_blinkit_reviews.csv"
TARGET = 500


def main() -> None:
    play = PlayStoreCollector().fetch(
        {"app_id": "com.grofers.customerapp", "lang": "en", "country": "in", "max_reviews": TARGET}
    )
    app = AppStoreCollector().fetch(
        {"app_id": "960335206", "country": "in", "max_reviews": max(50, TARGET - len(play))}
    )
    rows = []
    for item in play:
        rows.append(
            {
                "external_id": item.external_id or "",
                "text": item.text,
                "rating": item.rating if item.rating is not None else "",
                "source": "play_store",
            }
        )
    for item in app:
        rows.append(
            {
                "external_id": item.external_id or "",
                "text": item.text,
                "rating": item.rating if item.rating is not None else "",
                "source": "app_store",
            }
        )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["external_id", "text", "rating", "source"])
        writer.writeheader()
        writer.writerows(rows[:TARGET])
    print(f"Wrote {min(len(rows), TARGET)} reviews to {OUT}")


if __name__ == "__main__":
    main()
