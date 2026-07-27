"""Project sequencing and phase gate API."""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.implementation_prompts import (
    evaluate_implementation_prompts,
    get_implementation_prompt,
    implementation_prompts_summary,
)
from app.db.session import get_db
from app.services.key_risks import evaluate_key_risks
from app.services.phase_gates import evaluate_phases, sequencing_summary

router = APIRouter(prefix="/project", tags=["project"])


@router.get("/sequencing")
def get_sequencing() -> Dict[str, Any]:
    """Effort budget and dependency order (no DB checks)."""
    return sequencing_summary()


@router.get("/risks")
def get_risks(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Key risks from the implementation plan and automated mitigation status."""
    return evaluate_key_risks(db)


@router.get("/phases")
def get_phases(
    db: Session = Depends(get_db),
    through: int = Query(default=6, ge=1, le=6),
) -> Dict[str, Any]:
    """Automated gate status per phase through N."""
    return evaluate_phases(db, through=through)


@router.get("/implementation-prompts")
def get_implementation_prompts(
    phase: Optional[int] = Query(default=None, ge=1, le=6),
    validate: bool = Query(default=False, description="Include docs-first completeness checks"),
) -> Dict[str, Any]:
    """Sequential build prompts from implementation plan §10."""
    if validate:
        return evaluate_implementation_prompts()
    if phase is not None:
        prompt = get_implementation_prompt(phase)
        if prompt is None:
            raise HTTPException(status_code=404, detail=f"No prompt for phase {phase}")
        return prompt.to_dict()
    return implementation_prompts_summary()
