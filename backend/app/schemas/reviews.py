"""Review ingestion API schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PlayStoreIngestRequest(BaseModel):
    app_id: str = Field(default="com.grofers.customerapp")
    lang: str = "en"
    country: str = "in"
    max_reviews: int = Field(default=1000, ge=1, le=5000)


class AppStoreIngestRequest(BaseModel):
    app_id: str = Field(default="960335206")
    country: str = "in"
    max_reviews: int = Field(default=1000, ge=1, le=5000)


class ManualReviewItem(BaseModel):
    text: str = Field(min_length=1)
    rating: Optional[float] = None
    external_id: Optional[str] = None


class ManualReviewRequest(BaseModel):
    source_name: str = "manual_upload"
    reviews: List[ManualReviewItem] = Field(min_length=1)


class IngestResponse(BaseModel):
    run_id: int
    stats: Dict[str, Any]
    warnings: Optional[List[Dict[str, Any]]] = None


class ReviewStatsResponse(BaseModel):
    total_reviews: int
    by_source: List[Dict[str, Any]]


class RunSummary(BaseModel):
    id: int
    phase: str
    status: str
    stats_json: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
