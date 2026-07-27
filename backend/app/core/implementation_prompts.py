"""Sequential build prompts (implementation plan §10)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.phases import PHASES, get_phase


@dataclass(frozen=True)
class ImplementationPrompt:
    phase: int
    slug: str
    name: str
    summary: str
    cursor_prompt: str
    docs_first: tuple[str, ...]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


IMPLEMENTATION_PROMPTS: tuple[ImplementationPrompt, ...] = (
    ImplementationPrompt(
        1,
        "setup",
        "Project setup",
        "Repository scaffold, config, data models, migrations, logging, error handling, health endpoint.",
        "Implement Phase 1 — repository scaffold, config, data models, migrations, logging, error handling, health endpoint.",
        ("context.md", "architecture.md", "implementation-plan.md"),
    ),
    ImplementationPrompt(
        2,
        "collection",
        "Review collection",
        "Collector interface plus Play Store, App Store, CSV, JSON, and manual upload sources with run tracking.",
        "Implement Phase 2 — collector interface plus Play Store, App Store, CSV, JSON, and manual upload sources with run tracking.",
        ("workflow.md",),
    ),
    ImplementationPrompt(
        3,
        "preprocess",
        "Preprocessing and embeddings",
        "Cleaning, spam filtering, deduplication, language detection, translation, tokenisation, embeddings.",
        "Implement Phase 3 — cleaning, spam filtering, deduplication, language detection, translation, tokenisation, embeddings.",
        ("review-analysis.md",),
    ),
    ImplementationPrompt(
        4,
        "analysis",
        "LLM analysis and insights",
        "Groq client, versioned prompts, per-review analysis, clustering, insight generation, confidence scoring, ranking.",
        "Implement Phase 4 — Groq client, versioned prompts, per-review analysis, clustering, insight generation, confidence scoring, ranking.",
        ("review-analysis.md",),
    ),
    ImplementationPrompt(
        5,
        "research",
        "Research and validation",
        "Interview and survey repositories, affinity mapping, triangulation, opportunity assessment, problem definition.",
        "Implement Phase 5 — interview and survey repositories, affinity mapping, triangulation, opportunity assessment, problem definition.",
        (
            "research-plan.md",
            "interview-guide.md",
            "survey-plan.md",
            "problem-definition.md",
        ),
    ),
    ImplementationPrompt(
        6,
        "mvp",
        "MVP, deployment, and testing",
        "MVP recommendation engine, full dashboard, deployment, and test suite.",
        "Implement Phase 6 — MVP recommendation engine, full dashboard, deployment, and test suite.",
        (
            "mvp-design.md",
            "deployment-plan.md",
            "edge-cases.md",
            "testing-strategy.md",
        ),
    ),
)

POLICY_NOTE = (
    "Each prompt assumes the corresponding docs/ files already exist and are current "
    "(docs-first workflow per phase)."
)


def get_implementation_prompt(phase: int) -> Optional[ImplementationPrompt]:
    for prompt in IMPLEMENTATION_PROMPTS:
        if prompt.phase == phase:
            return prompt
    return None


def implementation_prompts_summary() -> Dict[str, Any]:
    return {
        "source": "implementation-plan.md §10",
        "policy": POLICY_NOTE,
        "total": len(IMPLEMENTATION_PROMPTS),
        "prompts": [p.to_dict() for p in IMPLEMENTATION_PROMPTS],
    }


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _docs_dir(root: Path) -> Path:
    return root / "docs"


@dataclass
class PromptCheck:
    check_id: str
    description: str
    passed: bool
    detail: str = ""


def evaluate_implementation_prompts(*, root: Optional[Path] = None) -> Dict[str, Any]:
    root = root or _repo_root()
    docs = _docs_dir(root)
    checks: List[PromptCheck] = []

    companion = docs / "implementation-prompts.md"
    checks.append(
        PromptCheck(
            "companion_doc",
            "implementation-prompts.md present under docs/",
            companion.is_file(),
            str(companion),
        )
    )

    count_ok = len(IMPLEMENTATION_PROMPTS) == len(PHASES)
    checks.append(
        PromptCheck(
            "prompt_count_matches_phases",
            "One implementation prompt per build phase (6)",
            count_ok,
            f"prompts={len(IMPLEMENTATION_PROMPTS)}, phases={len(PHASES)}",
        )
    )

    phase_slugs_ok = True
    for prompt in IMPLEMENTATION_PROMPTS:
        spec = get_phase(prompt.phase)
        if spec is None or spec.slug != prompt.slug:
            phase_slugs_ok = False
            break
    checks.append(
        PromptCheck(
            "prompt_phase_metadata",
            "Prompt phase numbers and slugs align with core.phases",
            phase_slugs_ok,
        )
    )

    missing_docs: List[str] = []
    for prompt in IMPLEMENTATION_PROMPTS:
        spec = get_phase(prompt.phase)
        if spec is None:
            continue
        for doc in spec.docs_first:
            if not (docs / doc).is_file():
                missing_docs.append(f"phase{prompt.phase}:{doc}")
    checks.append(
        PromptCheck(
            "docs_first_on_disk",
            "All docs-first files referenced by prompts exist",
            not missing_docs,
            f"missing={missing_docs}" if missing_docs else f"files={sum(len(p.docs_first) for p in IMPLEMENTATION_PROMPTS)}",
        )
    )

    cursor_prefix_ok = all(
        p.cursor_prompt.startswith(f"Implement Phase {p.phase}") for p in IMPLEMENTATION_PROMPTS
    )
    checks.append(
        PromptCheck(
            "cursor_prompt_format",
            "Each cursor_prompt starts with Implement Phase N",
            cursor_prefix_ok,
        )
    )

    complete = all(c.passed for c in checks)
    return {
        "source": "implementation-plan.md §10",
        "policy": POLICY_NOTE,
        "complete": complete,
        "checks": [asdict(c) for c in checks],
        "prompts": [p.to_dict() for p in IMPLEMENTATION_PROMPTS],
    }
