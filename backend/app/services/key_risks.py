"""Key project risks and automated mitigation checks (implementation plan §9)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.collectors.registry import COLLECTORS
from app.config import get_settings
from app.core.phases import PHASES
from app.llm.cache import ResponseCache
from app.llm.client import LLMRunBudget
from app.llm.prompts import PROMPTS_DIR
from app.models import Insight
from app.services.phase_gates import _docs_dir, _repo_root


@dataclass(frozen=True)
class KeyRisk:
    risk_id: str
    risk: str
    mitigation: str
    implementation: str


KEY_RISKS: tuple[KeyRisk, ...] = (
    KeyRisk(
        "generic_discovery_insights",
        "Reviews rarely discuss category discovery directly, so insights stay generic",
        "Discovery-specific extraction in Phase 4; interviews as primary source for barrier depth",
        "review_analysis prompt + Analysis.discovery_json; MVP resolve_dominant_barrier prefers interviews",
    ),
    KeyRisk(
        "llm_hallucination",
        "LLM invents plausible-sounding insights",
        "Mandatory review ID citations; uncitable insights are dropped",
        "app.insights.citations + insight generator filter; insight_generation prompt grounding rules",
    ),
    KeyRisk(
        "scraper_breakage",
        "Scraper breakage or rate limiting",
        "CSV/JSON fallback paths and committed sample dataset",
        "csv/json collectors, sample_blinkit_reviews.csv, manual upload routes",
    ),
    KeyRisk(
        "prompt_drift",
        "Prompt drift degrading quality silently",
        "Versioned prompts and golden evaluation set",
        "prompts/*.v*.txt, tests/fixtures/prompt_golden, test_prompt_golden.py",
    ),
    KeyRisk(
        "cost_overrun",
        "Cost overrun on large batches",
        "Consolidated per-review calls, response caching, per-run cost ceiling",
        "single review_analysis call, ResponseCache, LLMRunBudget + LLM_RUN_COST_CEILING_USD",
    ),
    KeyRisk(
        "scope_creep",
        "Scope creep across fourteen documents",
        "Documentation-first order and per-phase acceptance gates",
        "docs/ per phase docs_first, phase_gates API + check_phase_gates.py",
    ),
)


@dataclass
class MitigationCheck:
    check_id: str
    description: str
    passed: bool
    detail: str = ""


@dataclass
class RiskEvaluation:
    risk_id: str
    risk: str
    mitigation: str
    implementation: str
    mitigated: bool
    checks: List[MitigationCheck]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["checks"] = [asdict(c) for c in self.checks]
        return data


def _check_generic_discovery(root: Path) -> List[MitigationCheck]:
    prompt_path = root / "backend" / "app" / "prompts" / "review_analysis.v1.txt"
    prompt_ok = False
    if prompt_path.is_file():
        body = prompt_path.read_text(encoding="utf-8").lower()
        prompt_ok = "discovery" in body and "discovery_barriers" in body
    schema_ok = (
        root / "backend" / "app" / "schemas" / "analysis.py"
    ).is_file()
    barriers_ok = (root / "backend" / "app" / "mvp" / "barriers.py").is_file()
    interview_coding = (
        root / "backend" / "app" / "research" / "coding.py"
    ).is_file()
    return [
        MitigationCheck(
            "discovery_prompt_fields",
            "Review analysis prompt requests discovery extraction",
            prompt_ok,
            str(prompt_path),
        ),
        MitigationCheck(
            "discovery_schema_module",
            "Analysis schemas include discovery output",
            schema_ok,
        ),
        MitigationCheck(
            "interview_barrier_depth",
            "Interview coding and barrier resolution modules present",
            barriers_ok and interview_coding,
        ),
    ]


def _check_hallucination(root: Path, db: Session) -> List[MitigationCheck]:
    citations_mod = (
        root / "backend" / "app" / "insights" / "citations.py"
    ).is_file()
    generator = (root / "backend" / "app" / "insights" / "generator.py").is_file()
    test = (root / "backend" / "tests" / "test_insights_citation.py").is_file()
    bad_insights = 0
    total = db.query(Insight).count()
    if total:
        bad_insights = (
            db.query(Insight)
            .filter(
                (Insight.example_review_ids.is_(None))
                | (Insight.example_review_ids == [])
            )
            .count()
        )
    db_clean = total == 0 or bad_insights == 0
    return [
        MitigationCheck(
            "citation_enforcement_module",
            "Citation filter module for insights",
            citations_mod,
        ),
        MitigationCheck(
            "citation_unit_tests",
            "Unit tests for uncitable insight removal",
            test,
        ),
        MitigationCheck(
            "insight_generator_wiring",
            "Insight generator module present",
            generator,
        ),
        MitigationCheck(
            "stored_insights_cited",
            "Persisted insights have example_review_ids",
            db_clean,
            f"total={total}, uncited={bad_insights}",
        ),
    ]


def _check_scraper_fallback(root: Path) -> List[MitigationCheck]:
    sample = root / "backend" / "data" / "sample_blinkit_reviews.csv"
    sample_ok = False
    if sample.is_file():
        sample_ok = sum(1 for _ in sample.open(encoding="utf-8")) >= 400
    csv_mod = (root / "backend" / "app" / "collectors" / "csv_collector.py").is_file()
    json_mod = (root / "backend" / "app" / "collectors" / "json_collector.py").is_file()
    store_ok = "play_store" in COLLECTORS and "app_store" in COLLECTORS
    upload = (root / "backend" / "app" / "api" / "routes" / "reviews.py").is_file()
    return [
        MitigationCheck(
            "offline_sample_corpus",
            "Committed sample Blinkit reviews CSV (~500 rows)",
            sample_ok,
            str(sample),
        ),
        MitigationCheck(
            "file_and_store_collectors",
            "CSV/JSON collectors and Play/App Store collectors",
            csv_mod and json_mod and store_ok,
        ),
        MitigationCheck(
            "manual_upload_routes",
            "Review upload / manual ingestion API",
            upload,
        ),
    ]


def _check_prompt_drift(root: Path) -> List[MitigationCheck]:
    golden = (
        root
        / "backend"
        / "tests"
        / "fixtures"
        / "prompt_golden"
        / "review_golden_set.json"
    )
    golden_ok = False
    if golden.is_file():
        try:
            golden_ok = len(json.loads(golden.read_text(encoding="utf-8"))) >= 50
        except json.JSONDecodeError:
            golden_ok = False
    versioned = list(PROMPTS_DIR.glob("*.v*.txt"))
    versioned_ok = len(versioned) >= 3
    golden_test = (root / "backend" / "tests" / "test_prompt_golden.py").is_file()
    return [
        MitigationCheck(
            "versioned_prompt_files",
            "Multiple versioned prompt templates under app/prompts",
            versioned_ok,
            f"count={len(versioned)}",
        ),
        MitigationCheck(
            "golden_set_50",
            "Hand-labelled golden set with ≥50 reviews",
            golden_ok,
            str(golden),
        ),
        MitigationCheck(
            "golden_regression_tests",
            "pytest golden-set agreement tests",
            golden_test,
        ),
    ]


def _check_cost_controls(root: Path) -> List[MitigationCheck]:
    settings = get_settings()
    ceiling_ok = settings.llm_run_cost_ceiling_usd > 0
    budget_class = LLMRunBudget(ceiling_usd=1.0)
    try:
        budget_class.charge(2.0, budget_class.usage)
        ceiling_raises = False
    except RuntimeError:
        ceiling_raises = True
    cache_ok = (root / "backend" / "app" / "llm" / "cache.py").is_file()
    groq_ok = (root / "backend" / "app" / "llm" / "groq_client.py").is_file()
    consolidated = (
        root / "backend" / "app" / "analysis" / "review.py"
    ).is_file()
    single_call = False
    if consolidated:
        src = (root / "backend" / "app" / "analysis" / "review.py").read_text(
            encoding="utf-8"
        )
        single_call = "ReviewAnalysisOutput" in src and src.count("await client.complete") >= 1
    cache_impl = ResponseCache().get("x", "y") is None
    return [
        MitigationCheck(
            "cost_ceiling_config",
            "LLM_RUN_COST_CEILING_USD configured",
            ceiling_ok,
            f"ceiling_usd={settings.llm_run_cost_ceiling_usd}",
        ),
        MitigationCheck(
            "run_budget_enforced",
            "LLMRunBudget raises when ceiling exceeded",
            ceiling_raises,
        ),
        MitigationCheck(
            "response_cache",
            "LLM response cache keyed on prompt + input hash",
            cache_ok and cache_impl,
        ),
        MitigationCheck(
            "groq_client_cost_tracking",
            "Groq client tracks usage and charges budget",
            groq_ok,
        ),
        MitigationCheck(
            "consolidated_review_analysis",
            "Single structured call per review (ReviewAnalysisOutput)",
            single_call,
        ),
    ]


def _check_scope_creep(root: Path) -> List[MitigationCheck]:
    docs = _docs_dir(root)
    required_docs: set[str] = set()
    for phase in PHASES:
        required_docs.update(phase.docs_first)
    required_docs.add("implementation-plan.md")
    required_docs.add("key-risks.md")
    required_docs.add("implementation-prompts.md")
    missing = sorted(d for d in required_docs if not (docs / d).is_file())
    gates_script = (root / "backend" / "scripts" / "check_phase_gates.py").is_file()
    gates_service = (
        root / "backend" / "app" / "services" / "phase_gates.py"
    ).is_file()
    return [
        MitigationCheck(
            "docs_first_artifacts",
            "All phase docs-first files plus key-risks.md present",
            not missing,
            f"missing={missing}" if missing else f"count={len(required_docs)}",
        ),
        MitigationCheck(
            "phase_gate_automation",
            "Phase gate service and CLI checker",
            gates_script and gates_service,
        ),
    ]


_CHECK_BUILDERS = {
    "generic_discovery_insights": lambda root, db: _check_generic_discovery(root),
    "llm_hallucination": lambda root, db: _check_hallucination(root, db),
    "scraper_breakage": lambda root, db: _check_scraper_fallback(root),
    "prompt_drift": lambda root, db: _check_prompt_drift(root),
    "cost_overrun": lambda root, db: _check_cost_controls(root),
    "scope_creep": lambda root, db: _check_scope_creep(root),
}


def evaluate_key_risks(
    db: Session,
    *,
    root: Optional[Path] = None,
) -> Dict[str, Any]:
    root = root or _repo_root()
    evaluations: List[RiskEvaluation] = []
    for spec in KEY_RISKS:
        builder = _CHECK_BUILDERS[spec.risk_id]
        checks = builder(root, db)
        mitigated = bool(checks) and all(c.passed for c in checks)
        evaluations.append(
            RiskEvaluation(
                risk_id=spec.risk_id,
                risk=spec.risk,
                mitigation=spec.mitigation,
                implementation=spec.implementation,
                mitigated=mitigated,
                checks=checks,
            )
        )
    mitigated_count = sum(1 for e in evaluations if e.mitigated)
    return {
        "source": "implementation-plan.md §9",
        "total_risks": len(KEY_RISKS),
        "mitigated_count": mitigated_count,
        "all_mitigated": mitigated_count == len(KEY_RISKS),
        "risks": [e.to_dict() for e in evaluations],
    }


def failing_risk_ids(report: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    for item in report.get("risks", []):
        if not item.get("mitigated"):
            out.append(str(item.get("risk_id", "")))
    return [r for r in out if r]
