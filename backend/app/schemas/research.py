"""Pydantic schemas for research repository APIs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class InterviewCreate(BaseModel):
    participant_segment: Optional[str] = None
    transcript: str = Field(min_length=20)
    notes: Optional[str] = None
    conducted_at: Optional[datetime] = None


class InterviewSummary(BaseModel):
    id: int
    participant_segment: Optional[str] = None
    conducted_at: Optional[datetime] = None
    coding_version: Optional[str] = None
    has_coding: bool = False
    jtbd: Optional[str] = None
    pain_points: Optional[str] = None

    model_config = {"from_attributes": True}


class InterviewDetail(InterviewSummary):
    transcript: Optional[str] = None
    notes: Optional[str] = None
    coding_json: Optional[Dict[str, Any]] = None


class CodedQuote(BaseModel):
    quote: str
    transcript_start: int = Field(ge=0)
    transcript_end: int = Field(gt=0)
    theme_category: str


class InterviewCodingOutput(BaseModel):
    pain_points: List[str] = Field(default_factory=list)
    jtbd: str
    discovery_barriers: List[str] = Field(default_factory=list)
    theme_categories: List[str] = Field(default_factory=list)
    quotes: List[CodedQuote] = Field(default_factory=list)


class SurveyRow(BaseModel):
    id: int
    question: str
    response: str
    respondent_segment: Optional[str] = None
    submitted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SurveyAggregateItem(BaseModel):
    question_key: str
    response: str
    count: int
    segments: Dict[str, int] = Field(default_factory=dict)


class AffinityGroup(BaseModel):
    theme_category: str
    sources: List[str]
    finding_count: int
    sample_quotes: List[str] = Field(default_factory=list)
    discovery_barriers: List[str] = Field(default_factory=list)


class TriangulationResult(BaseModel):
    insight_id: int
    status: str
    human_evidence: str
    interview_ids: List[int] = Field(default_factory=list)
    survey_support_count: int = 0


class OpportunityScore(BaseModel):
    id: int
    title: str
    insight_id: Optional[int] = None
    reach_score: float
    severity_score: float
    north_star_score: float
    effort_score: float
    total_score: float
    scoring_rationale: Dict[str, Any]
    rank: int

    model_config = {"from_attributes": True}


class ResearchRunResponse(BaseModel):
    run_id: int
    stats: Dict[str, Any]


class ProblemDefinitionResponse(BaseModel):
    path: str
    markdown: str


class SeedResearchResponse(BaseModel):
    interviews_loaded: int
    survey_rows_loaded: int
