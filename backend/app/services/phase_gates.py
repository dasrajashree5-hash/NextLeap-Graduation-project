"""Automated phase gate evaluation."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.collectors.registry import COLLECTORS
from app.core.phases import (
    DEFAULT_PROJECT_HOURS,
    PHASES,
    SEQUENCING_POLICY,
    effort_hours,
    get_phase,
    total_effort_pct,
)
from app.models import Insight, Interview, Review


@dataclass
class GateCheck:
    gate_id: str
    description: str
    passed: Optional[bool]
    detail: str
    manual: bool = False


@dataclass
class PhaseEvaluation:
    phase: int
    slug: str
    name: str
    effort_pct: float
    effort_hours: float
    depends_on: List[int]
    docs_first: List[str]
    parallel_tracks: List[str]
    unlocked: bool
    automated_complete: bool
    gates: List[GateCheck]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["gates"] = [asdict(g) for g in self.gates]
        return data


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _docs_dir(root: Path) -> Path:
    return root / "docs"


def _doc_exists(root: Path, name: str) -> bool:
    return (_docs_dir(root) / name).is_file()


def _table_exists(db: Session, name: str) -> bool:
    try:
        return inspect(db.get_bind()).has_table(name)
    except Exception:  # noqa: BLE001
        return False


def _gate(
    gate_id: str,
    description: str,
    passed: bool,
    detail: str = "",
    *,
    manual: bool = False,
) -> GateCheck:
    return GateCheck(
        gate_id=gate_id,
        description=description,
        passed=None if manual else passed,
        detail=detail,
        manual=manual,
    )


def _check_database(db: Session) -> tuple[str, str]:
    try:
        db.execute(text("SELECT 1"))
        return "ok", ""
    except Exception as exc:  # noqa: BLE001
        return "error", str(exc)


def _phase1_gates(db: Session, root: Path) -> List[GateCheck]:
    db_status, db_detail = _check_database(db)
    tables = all(_table_exists(db, t) for t in ("sources", "reviews", "runs", "insights"))
    docs = all(_doc_exists(root, d) for d in ("context.md", "architecture.md", "implementation-plan.md"))
    docker = (root / "docker-compose.yml").is_file()
    return [
        _gate("p1_health_database", "Database reachable via health checks", db_status == "ok", db_detail or ""),
        _gate("p1_schema_tables", "Core SQLAlchemy tables exist", tables, "sources,reviews,runs,insights"),
        _gate("p1_docs", "Phase 1 docs present", docs, "context, architecture, implementation-plan"),
        _gate("p1_docker_compose", "docker-compose.yml committed", docker),
        _gate(
            "p1_no_secrets",
            "No real secrets committed (manual audit)",
            True,
            manual=True,
        ),
        _gate(
            "p1_frontend_shell",
            "Next.js dashboard shell renders (manual)",
            True,
            manual=True,
        ),
    ]


def _phase2_gates(db: Session, root: Path) -> List[GateCheck]:
    sample = root / "backend" / "data" / "sample_blinkit_reviews.csv"
    sample_ok = sample.is_file() and sum(1 for _ in sample.open(encoding="utf-8")) >= 400
    collectors = "play_store" in COLLECTORS and "app_store" in COLLECTORS
    csv_mod = (root / "backend" / "app" / "collectors" / "csv_collector.py").is_file()
    json_mod = (root / "backend" / "app" / "collectors" / "json_collector.py").is_file()
    routes = (root / "backend" / "app" / "api" / "routes" / "reviews.py").is_file()
    review_count = db.query(Review).count()
    return [
        _gate("p2_sample_corpus", "Offline sample CSV (~500 rows)", sample_ok, str(sample)),
        _gate("p2_store_collectors", "Play Store and App Store collectors registered", collectors),
        _gate("p2_file_collectors", "CSV and JSON collectors implemented", csv_mod and json_mod),
        _gate("p2_ingest_routes", "Review ingestion API routes present", routes),
        _gate(
            "p2_review_data",
            "Reviews persisted in database",
            review_count >= 1,
            f"count={review_count}",
        ),
        _gate(
            "p2_live_1000_reviews",
            "≥1,000 live store reviews ingested (manual / ops)",
            True,
            manual=True,
        ),
        _gate(
            "p2_dedupe_rerun",
            "Re-ingest adds zero duplicates (manual / integration)",
            True,
            manual=True,
        ),
    ]


def _phase3_gates(db: Session, root: Path) -> List[GateCheck]:
    pipeline = (root / "backend" / "app" / "api" / "routes" / "pipeline.py").is_file()
    clean = (root / "backend" / "app" / "preprocessing" / "clean.py").is_file()
    dedupe = (root / "backend" / "app" / "preprocessing" / "dedupe.py").is_file()
    preprocess_test = (
        root / "backend" / "tests" / "test_pipeline.py"
    ).is_file()
    has_preprocessed_row = (
        db.query(Review).filter(Review.clean_text.isnot(None)).first() is not None
    )
    return [
        _gate("p3_preprocess_api", "Preprocess pipeline API present", pipeline),
        _gate("p3_cleaning_module", "Cleaning module present", clean),
        _gate("p3_dedupe_module", "Dedupe module present", dedupe),
        _gate("p3_idempotent_test", "Idempotent preprocess test exists", preprocess_test),
        _gate(
            "p3_preprocessed_rows",
            "At least one review preprocessed in DB",
            has_preprocessed_row,
            "run POST /api/pipeline/preprocess",
        ),
        _gate(
            "p3_performance_10k",
            "10k reviews preprocess <5 min (manual / slow test)",
            True,
            manual=True,
        ),
        _gate(
            "p3_duplicate_rate",
            "Duplicate rate <1% spot-check (manual)",
            True,
            manual=True,
        ),
    ]


def _phase4_gates(db: Session, root: Path) -> List[GateCheck]:
    prompt = (root / "backend" / "app" / "prompts" / "review_analysis.v1.txt").is_file()
    insights_route = (root / "backend" / "app" / "api" / "routes" / "insights.py").is_file()
    golden = root / "backend" / "tests" / "fixtures" / "prompt_golden" / "review_golden_set.json"
    golden_ok = False
    if golden.is_file():
        try:
            golden_ok = len(json.loads(golden.read_text())) >= 50
        except json.JSONDecodeError:
            golden_ok = False
    insight_count = db.query(Insight).count()
    theme_route = (root / "backend" / "app" / "api" / "routes" / "themes.py").is_file()
    return [
        _gate("p4_versioned_prompts", "Versioned review analysis prompt", prompt),
        _gate("p4_insights_api", "Insights API routes present", insights_route),
        _gate("p4_themes_api", "Themes API routes present", theme_route),
        _gate("p4_golden_set", "Prompt golden set (≥50 rows)", golden_ok, str(golden)),
        _gate(
            "p4_insights_generated",
            "≥15 insights with required fields (manual / pipeline)",
            True,
            f"db_count={insight_count}",
            manual=True,
        ),
        _gate(
            "p4_analyze_1k",
            "1k reviews analyzed <2% failure (manual)",
            True,
            manual=True,
        ),
        _gate(
            "p4_blind_review",
            "Blind manual review of 10 insights (manual)",
            True,
            manual=True,
        ),
    ]


def _phase5_gates(db: Session, root: Path) -> List[GateCheck]:
    docs = all(
        _doc_exists(root, d)
        for d in (
            "research-plan.md",
            "interview-guide.md",
            "survey-plan.md",
            "problem-definition.md",
        )
    )
    triangulation = (root / "backend" / "app" / "research" / "triangulation.py").is_file()
    interviews = db.query(Interview).count()
    insights_validated = (
        db.query(Insight).filter(Insight.validation_status.isnot(None)).count() >= 1
    )
    return [
        _gate("p5_research_docs", "Phase 5 research docs present", docs),
        _gate("p5_triangulation", "Triangulation engine implemented", triangulation),
        _gate(
            "p5_interviews_stored",
            "≥5 interviews stored (seed or upload)",
            interviews >= 5,
            f"count={interviews}",
        ),
        _gate(
            "p5_insight_validation",
            "Insights carry validation status",
            insights_validated,
            "triangulate or generate insights first",
        ),
        _gate(
            "p5_rejection_example",
            "At least one insight rejected by interviews (manual)",
            True,
            manual=True,
        ),
        _gate(
            "p5_top_opportunities",
            "Top 3 opportunities with scoring rationale (manual)",
            True,
            manual=True,
        ),
    ]


def _phase6_gates(db: Session, root: Path) -> List[GateCheck]:
    mvp = (root / "backend" / "app" / "api" / "routes" / "mvp.py").is_file()
    ci = (root / ".github" / "workflows" / "ci.yml").is_file()
    testing_doc = _doc_exists(root, "testing-strategy.md")
    streamlit = (root / "streamlit_app" / "app.py").is_file()
    deploy_doc = _doc_exists(root, "deployment-plan.md")
    return [
        _gate("p6_mvp_api", "MVP API routes present", mvp),
        _gate("p6_ci_pipeline", "GitHub Actions CI workflow", ci),
        _gate("p6_testing_strategy", "testing-strategy.md documented", testing_doc),
        _gate("p6_streamlit", "Streamlit Case 1 app", streamlit),
        _gate("p6_deployment_plan", "deployment-plan.md present", deploy_doc),
        _gate(
            "p6_public_deploy",
            "Public URL demo on seeded data (manual)",
            True,
            manual=True,
        ),
        _gate(
            "p6_lighthouse",
            "Lighthouse accessibility ≥90 (manual)",
            True,
            manual=True,
        ),
        _gate(
            "p6_rollback",
            "Rollback demonstrated once (manual)",
            True,
            manual=True,
        ),
    ]


_GATE_BUILDERS: Dict[int, Callable[[Session, Path], List[GateCheck]]] = {
    1: _phase1_gates,
    2: _phase2_gates,
    3: _phase3_gates,
    4: _phase4_gates,
    5: _phase5_gates,
    6: _phase6_gates,
}


def _automated_complete(gates: List[GateCheck]) -> bool:
    auto = [g for g in gates if not g.manual]
    return bool(auto) and all(g.passed for g in auto)


def _phase_unlocked(phase_num: int, completed_phases: set[int]) -> bool:
    spec = get_phase(phase_num)
    if not spec:
        return False
    if not spec.depends_on:
        return True
    return all(dep in completed_phases for dep in spec.depends_on)


def evaluate_phases(
    db: Session,
    *,
    through: int = 6,
    project_hours: Optional[float] = None,
) -> Dict[str, Any]:
    root = _repo_root()
    hours = project_hours
    if hours is None:
        hours = float(os.getenv("PROJECT_EFFORT_HOURS", DEFAULT_PROJECT_HOURS))

    evaluations: List[PhaseEvaluation] = []
    for spec in PHASES:
        if spec.number > through:
            break
        builder = _GATE_BUILDERS.get(spec.number)
        gates = builder(db, root) if builder else []
        ev = PhaseEvaluation(
            phase=spec.number,
            slug=spec.slug,
            name=spec.name,
            effort_pct=spec.effort_pct,
            effort_hours=effort_hours(spec.effort_pct, hours),
            depends_on=list(spec.depends_on),
            docs_first=list(spec.docs_first),
            parallel_tracks=list(spec.parallel_tracks),
            unlocked=False,
            automated_complete=_automated_complete(gates),
            gates=gates,
        )
        evaluations.append(ev)

    completed = {e.phase for e in evaluations if e.automated_complete}
    for ev in evaluations:
        ev.unlocked = _phase_unlocked(ev.phase, completed)

    current = 1
    for ev in evaluations:
        if ev.automated_complete:
            current = ev.phase + 1
        else:
            current = ev.phase
            break
    else:
        current = through + 1 if evaluations else 1

    return {
        "sequencing": SEQUENCING_POLICY,
        "total_effort_pct": total_effort_pct(),
        "project_effort_hours": hours,
        "recommended_current_phase": min(current, 6),
        "phases": [e.to_dict() for e in evaluations],
    }


def sequencing_summary(project_hours: Optional[float] = None) -> Dict[str, Any]:
    hours = project_hours or float(os.getenv("PROJECT_EFFORT_HOURS", DEFAULT_PROJECT_HOURS))
    return {
        "policy": SEQUENCING_POLICY,
        "total_effort_pct": total_effort_pct(),
        "project_effort_hours": hours,
        "phases": [
            {
                "phase": p.number,
                "slug": p.slug,
                "name": p.name,
                "focus": p.focus,
                "effort_pct": p.effort_pct,
                "effort_hours": effort_hours(p.effort_pct, hours),
                "depends_on": list(p.depends_on),
                "docs_first": list(p.docs_first),
                "parallel_tracks": list(p.parallel_tracks),
            }
            for p in PHASES
        ],
    }
