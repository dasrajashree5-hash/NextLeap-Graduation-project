"""Analysis pipeline API schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    limit: int = Field(default=100, ge=1, le=5000)
    force: bool = False


class ClusterRequest(BaseModel):
    force: bool = False
    min_cluster_size: int = Field(default=5, ge=3, le=50)


class InsightsRequest(BaseModel):
    replace: bool = True


class PipelineRunResponse(BaseModel):
    run_id: int
    stats: Dict[str, Any]


class AnalysisStatusResponse(BaseModel):
    analysis_version: str
    pending_analysis: int
    analyzed_reviews: int
    failed_analysis: int
    themes: int
    insights: int


class InsightResponse(BaseModel):
    id: int
    problem: str
    evidence: Optional[str]
    frequency: Optional[int]
    example_review_ids: Optional[List[int]]
    customer_segment: Optional[str]
    business_impact: Optional[str]
    opportunity: Optional[str]
    confidence_score: Optional[float]
    confidence_breakdown: Optional[Dict[str, Any]]
    rank_score: Optional[float]
    validation_status: Optional[str]
    theme_id: Optional[int]


class ThemeResponse(BaseModel):
    id: int
    label: str
    description: Optional[str]
    category: Optional[str]
    review_count: int
