"""Generate docs/problem-definition.md from triangulated evidence."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Insight, Interview, Opportunity, Validation
from app.research.affinity import build_affinity_map
from app.research.surveys import aggregate_surveys


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def generate_problem_definition_markdown(db: Session) -> str:
    opportunities: List[Opportunity] = (
        db.query(Opportunity).order_by(Opportunity.rank.asc()).limit(3).all()
    )
    insights = (
        db.query(Insight)
        .filter(Insight.validation_status.in_(["validated", "partially_supported", "rejected"]))
        .order_by(Insight.rank_score.desc())
        .limit(8)
        .all()
    )
    interviews = db.query(Interview).count()
    survey_agg = aggregate_surveys(db)[:6]
    affinity = build_affinity_map(db)[:5]

    lines = [
        "# Problem Definition",
        "",
        "**Project:** AI-Powered Product Discovery Engine for Blinkit",
        "**Status:** Generated from triangulated review, interview, and survey evidence",
        "",
        "---",
        "",
        "## North star",
        "",
        "Increase the share of Blinkit baskets that include at least one **adjacent-category** item",
        "the shopper has not purchased in the prior 90 days, without increasing time-to-checkout.",
        "",
        "## Sharpened problem",
        "",
        "Blinkit shoppers treat the app as a **mission-driven restock tool**: they search for known SKUs,",
        "repeat prior baskets, and rarely explore non-grocery categories—even when latent demand exists",
        "(pet care, baby care, personal care expansions). Discovery fails at the **moment of purchase**",
        "because in-flow surfaces do not reduce trust and habit barriers with contextual, cited suggestions.",
        "",
        "## Evidence summary",
        "",
        f"- **Interviews coded:** {interviews}",
        f"- **Survey aggregates:** {len(survey_agg)} question/response buckets loaded",
        f"- **AI insights triangulated:** {db.query(Insight).count()}",
        "",
        "### Top affinity themes (human + AI)",
        "",
    ]
    for group in affinity:
        lines.append(
            f"- **{group['theme_category']}** — {group['finding_count']} findings "
            f"({', '.join(group['sources'][:3])})"
        )

    lines.extend(["", "### Validated / contested AI insights", ""])
    for ins in insights:
        val = ins.validation_status or "unknown"
        review_ids = ins.example_review_ids or []
        lines.append(f"- **[{val}]** {ins.problem}")
        lines.append(f"  - Reviews cited: `{review_ids[:6]}`")
        vrows = (
            db.query(Validation)
            .filter(Validation.insight_id == ins.id, Validation.source_type == "interview")
            .all()
        )
        if vrows and vrows[0].notes:
            lines.append(f"  - Interview evidence: {vrows[0].notes[:240]}")

    lines.extend(["", "### Ranked opportunities", ""])
    for opp in opportunities:
        lines.append(f"{opp.rank}. **{opp.title}** (score {opp.total_score})")
        rat = opp.scoring_rationale or {}
        lines.append(
            f"   - Reach {opp.reach_score}, Severity {opp.severity_score}, "
            f"North-star {opp.north_star_score}, Effort {opp.effort_score}"
        )
        if rat.get("weights"):
            lines.append(f"   - Weights: {rat['weights']}")

    lines.extend(
        [
            "",
            "## Implications for MVP",
            "",
            "Ship a **barrier-aware, in-cart suggestion** with one adjacent item per order,",
            "grounded in insight IDs and human quotes—not generic promotions.",
            "",
            "## Rejected assumptions",
            "",
            "Any insight marked `rejected` above should not drive MVP copy; interviews outrank",
            "stated survey enthusiasm for AI when behaviors describe dismissal and trust barriers.",
            "",
        ]
    )
    return "\n".join(lines)


def write_problem_definition(db: Session, path: Optional[Path] = None) -> tuple[str, str]:
    markdown = generate_problem_definition_markdown(db)
    root = _project_root()
    out_path = path or (root / "docs" / "problem-definition.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(markdown, encoding="utf-8")
    return str(out_path), markdown
