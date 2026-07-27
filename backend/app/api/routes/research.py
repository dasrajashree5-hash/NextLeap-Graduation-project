"""Research repository routes — interviews, surveys, triangulation."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.errors import ValidationError
from app.db.session import get_db
from app.models import Interview, Survey
from app.research.affinity import build_affinity_map
from app.research.coding import code_interview, run_code_all
from app.research.interviews import (
    bulk_create_interviews,
    create_interview,
    parse_interview_upload,
)
from app.research.opportunity import list_opportunities, run_opportunity_assessment
from app.research.problem_definition import write_problem_definition
from app.research.seed import seed_research
from app.research.surveys import aggregate_surveys, ingest_survey_csv
from app.research.triangulation import run_triangulation
from app.schemas.research import (
    AffinityGroup,
    InterviewCreate,
    InterviewDetail,
    InterviewSummary,
    OpportunityScore,
    ProblemDefinitionResponse,
    ResearchRunResponse,
    SeedResearchResponse,
    SurveyAggregateItem,
    SurveyRow,
)

router = APIRouter()


def _project_root() -> Path:
    return Path(__file__).resolve().parents[4]


@router.get("/interviews", response_model=List[InterviewSummary])
def list_interviews(db: Session = Depends(get_db)) -> List[InterviewSummary]:
    rows = db.query(Interview).order_by(Interview.id.desc()).all()
    return [
        InterviewSummary(
            id=r.id,
            participant_segment=r.participant_segment,
            conducted_at=r.conducted_at,
            coding_version=r.coding_version,
            has_coding=bool(r.coding_json),
            jtbd=r.jtbd,
            pain_points=r.pain_points,
        )
        for r in rows
    ]


@router.get("/interviews/{interview_id}", response_model=InterviewDetail)
def get_interview(interview_id: int, db: Session = Depends(get_db)) -> InterviewDetail:
    row = db.query(Interview).filter(Interview.id == interview_id).first()
    if not row:
        raise ValidationError("Interview not found", details=[{"id": interview_id}])
    return InterviewDetail(
        id=row.id,
        participant_segment=row.participant_segment,
        conducted_at=row.conducted_at,
        coding_version=row.coding_version,
        has_coding=bool(row.coding_json),
        jtbd=row.jtbd,
        pain_points=row.pain_points,
        transcript=row.transcript,
        notes=row.notes,
        coding_json=row.coding_json,
    )


@router.post("/interviews", response_model=InterviewSummary)
def post_interview(
    body: InterviewCreate,
    db: Session = Depends(get_db),
) -> InterviewSummary:
    row = create_interview(
        db,
        transcript=body.transcript,
        participant_segment=body.participant_segment,
        notes=body.notes,
        conducted_at=body.conducted_at,
    )
    return InterviewSummary(
        id=row.id,
        participant_segment=row.participant_segment,
        conducted_at=row.conducted_at,
        coding_version=row.coding_version,
        has_coding=bool(row.coding_json),
        jtbd=row.jtbd,
        pain_points=row.pain_points,
    )


@router.post("/interviews/upload")
async def upload_interviews(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    content = await file.read()
    items, errors = parse_interview_upload(content, file.filename or "upload.txt")
    if errors:
        raise ValidationError("Interview upload failed", details=errors)
    count = bulk_create_interviews(db, items)
    return {"loaded": count}


@router.post("/interviews/{interview_id}/code", response_model=ResearchRunResponse)
def code_one_interview(
    interview_id: int,
    use_llm: bool = Form(True),
    db: Session = Depends(get_db),
) -> ResearchRunResponse:
    row = db.query(Interview).filter(Interview.id == interview_id).first()
    if not row:
        raise ValidationError("Interview not found", details=[{"id": interview_id}])
    code_interview(db, row, use_llm=use_llm)
    return ResearchRunResponse(run_id=0, stats={"coded": 1, "interview_id": interview_id})


@router.post("/interviews/code-all", response_model=ResearchRunResponse)
def code_all_interviews(
    use_llm: bool = False,
    db: Session = Depends(get_db),
) -> ResearchRunResponse:
    result = run_code_all(db, use_llm=use_llm)
    return ResearchRunResponse(run_id=result["run_id"], stats=result["stats"])


@router.post("/surveys/upload")
async def upload_survey(
    file: UploadFile = File(...),
    replace: bool = Form(True),
    db: Session = Depends(get_db),
):
    content = await file.read()
    stats = ingest_survey_csv(db, content, replace=replace)
    return stats


@router.get("/surveys", response_model=List[SurveyRow])
def list_surveys(
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[SurveyRow]:
    rows = db.query(Survey).order_by(Survey.id.desc()).limit(limit).all()
    return rows


@router.get("/surveys/aggregate", response_model=List[SurveyAggregateItem])
def survey_aggregate(db: Session = Depends(get_db)) -> List[SurveyAggregateItem]:
    return aggregate_surveys(db)


@router.get("/affinity", response_model=List[AffinityGroup])
def affinity_map(db: Session = Depends(get_db)) -> List[AffinityGroup]:
    return build_affinity_map(db)


@router.post("/triangulate", response_model=ResearchRunResponse)
def triangulate(db: Session = Depends(get_db)) -> ResearchRunResponse:
    stats = run_triangulation(db)
    return ResearchRunResponse(run_id=0, stats=stats)


@router.post("/opportunities", response_model=ResearchRunResponse)
def assess_opportunities(db: Session = Depends(get_db)) -> ResearchRunResponse:
    result = run_opportunity_assessment(db)
    return ResearchRunResponse(run_id=result["run_id"], stats=result["stats"])


@router.get("/opportunities", response_model=List[OpportunityScore])
def get_opportunities(
    limit: int = 10,
    db: Session = Depends(get_db),
) -> List[OpportunityScore]:
    return list_opportunities(db, limit=limit)


@router.post("/problem-definition/generate", response_model=ProblemDefinitionResponse)
def generate_problem_definition(db: Session = Depends(get_db)) -> ProblemDefinitionResponse:
    path, markdown = write_problem_definition(db)
    return ProblemDefinitionResponse(path=path, markdown=markdown)


@router.get("/problem-definition", response_model=ProblemDefinitionResponse)
def read_problem_definition(db: Session = Depends(get_db)) -> ProblemDefinitionResponse:
    path, markdown = write_problem_definition(db)
    return ProblemDefinitionResponse(path=path, markdown=markdown)


@router.post("/seed", response_model=SeedResearchResponse)
def seed_sample_research(
    code: bool = True,
    db: Session = Depends(get_db),
) -> SeedResearchResponse:
    stats = seed_research(db, _project_root(), code=code)
    return SeedResearchResponse(
        interviews_loaded=stats["interviews_loaded"],
        survey_rows_loaded=stats["survey_rows_loaded"],
    )
