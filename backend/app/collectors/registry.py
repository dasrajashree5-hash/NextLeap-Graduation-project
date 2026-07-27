"""Collector registry."""

from typing import Any, Dict, Type

from app.collectors.app_store import AppStoreCollector
from app.collectors.play_store import PlayStoreCollector

COLLECTORS: Dict[str, Any] = {
    "play_store": PlayStoreCollector(),
    "app_store": AppStoreCollector(),
}


def get_store_collector(source_type: str):
    collector = COLLECTORS.get(source_type)
    if not collector:
        raise KeyError(f"Unknown collector: {source_type}")
    return collector
