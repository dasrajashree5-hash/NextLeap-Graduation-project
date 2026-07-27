"""Shared collector types."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class RawReview:
    text: str
    external_id: Optional[str] = None
    rating: Optional[float] = None
    posted_at: Optional[datetime] = None
    author_hash: Optional[str] = None
    raw_payload: Dict[str, Any] = field(default_factory=dict)


class BaseCollector(ABC):
    source_type: str

    @abstractmethod
    def fetch(self, config: Dict[str, Any]) -> List[RawReview]:
        raise NotImplementedError
