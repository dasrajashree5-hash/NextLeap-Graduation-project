"""Build phase metadata (sequencing and effort)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

DEFAULT_PROJECT_HOURS = 120


@dataclass(frozen=True)
class PhaseSpec:
    number: int
    slug: str
    name: str
    focus: str
    effort_pct: float
    depends_on: tuple[int, ...] = ()
    docs_first: tuple[str, ...] = ()
    parallel_tracks: tuple[str, ...] = ()


PHASES: tuple[PhaseSpec, ...] = (
    PhaseSpec(
        1,
        "setup",
        "Project setup",
        "Repository scaffold, config, models, health",
        10.0,
        docs_first=("context.md", "architecture.md", "implementation-plan.md"),
    ),
    PhaseSpec(
        2,
        "collection",
        "Review collection",
        "Collectors, ingestion API, sample corpus",
        15.0,
        depends_on=(1,),
        docs_first=("workflow.md",),
        parallel_tracks=("frontend_dashboard_scaffold",),
    ),
    PhaseSpec(
        3,
        "preprocess",
        "Preprocessing and embeddings",
        "Clean, dedupe, language, translate, embed",
        15.0,
        depends_on=(2,),
        docs_first=("review-analysis.md",),
    ),
    PhaseSpec(
        4,
        "analysis",
        "LLM analysis and insights",
        "Groq client, prompts, clustering, insights",
        30.0,
        depends_on=(3,),
        docs_first=("review-analysis.md",),
    ),
    PhaseSpec(
        5,
        "research",
        "Research and validation",
        "Interviews, surveys, triangulation, opportunities",
        15.0,
        depends_on=(4,),
        docs_first=(
            "research-plan.md",
            "interview-guide.md",
            "survey-plan.md",
            "problem-definition.md",
        ),
    ),
    PhaseSpec(
        6,
        "mvp",
        "MVP, deployment, and testing",
        "Recommendation engine, dashboard, CI, deploy",
        15.0,
        depends_on=(5,),
        docs_first=(
            "mvp-design.md",
            "deployment-plan.md",
            "edge-cases.md",
            "testing-strategy.md",
        ),
        parallel_tracks=("frontend_live_api_polish",),
    ),
)

SEQUENCING_POLICY = {
    "mode": "strict_sequential",
    "exception": "frontend_scaffolding_parallel_from_phase_2",
    "description": (
        "Backend phases run in order 1→6. Frontend may scaffold against mocks from phase 2; "
        "production wiring completes in phase 6."
    ),
}


def effort_hours(effort_pct: float, total_hours: float = DEFAULT_PROJECT_HOURS) -> float:
    return round(total_hours * effort_pct / 100.0, 1)


def get_phase(number: int) -> Optional[PhaseSpec]:
    for p in PHASES:
        if p.number == number:
            return p
    return None


def total_effort_pct() -> float:
    return sum(p.effort_pct for p in PHASES)
