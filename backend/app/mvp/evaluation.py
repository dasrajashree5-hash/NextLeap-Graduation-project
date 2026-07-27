"""Held-out basket evaluation for MVP suggestion quality."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models import Insight, Run
from app.mvp.engine import recommend_for_basket
from app.schemas.mvp import BasketItem, EvalBasketCase, EvalCaseResult, EvalSummary


def _data_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "mvp_eval_baskets.json"


def load_eval_baskets(path: Optional[Path] = None) -> List[EvalBasketCase]:
    p = path or _data_path()
    raw = json.loads(p.read_text(encoding="utf-8"))
    return [EvalBasketCase.model_validate(row) for row in raw]


def _category_relevant(suggested: str, expected: List[str]) -> bool:
    if not suggested:
        return False
    if suggested in expected:
        return True
    # Allow partial token overlap for compound categories
    sug_tokens = set(suggested.lower().replace("&", " ").split())
    for exp in expected:
        exp_tokens = set(exp.lower().replace("&", " ").split())
        if sug_tokens & exp_tokens:
            return True
    return False


def _score_case(
    db: Session,
    case: EvalBasketCase,
    *,
    limit: int = 1,
) -> EvalCaseResult:
    items = [BasketItem(name=i.name, category=i.category) for i in case.items]
    response = recommend_for_basket(
        db,
        basket_items=items,
        customer_segment=case.customer_segment,
        limit=limit,
    )
    notes: List[str] = []
    if not response.suggestions:
        return EvalCaseResult(
            case_id=case.id,
            passed=False,
            suggested_category=None,
            insight_id=None,
            category_relevant=False,
            insight_cited=False,
            insight_non_rejected=False,
            message_present=False,
            notes=["no_suggestion"],
        )

    top = response.suggestions[0]
    insight = db.query(Insight).filter(Insight.id == top.insight_id).first()
    category_ok = _category_relevant(top.category, case.expected_adjacent_categories)
    cited = insight is not None
    non_rejected = cited and (insight.validation_status or "") not in (
        "rejected",
        "contradicting",
    )
    msg_ok = bool(top.message and top.message.strip())

    if not category_ok:
        notes.append("category_miss")
    if not cited:
        notes.append("missing_insight")
    if cited and not non_rejected:
        notes.append("rejected_insight")
    if not msg_ok:
        notes.append("empty_message")

    passed = category_ok and cited and non_rejected and msg_ok
    return EvalCaseResult(
        case_id=case.id,
        passed=passed,
        suggested_category=top.category,
        insight_id=top.insight_id,
        category_relevant=category_ok,
        insight_cited=cited,
        insight_non_rejected=non_rejected,
        message_present=msg_ok,
        notes=notes,
    )


def run_evaluation(
    db: Session,
    *,
    limit: int = 1,
    basket_ids: Optional[List[str]] = None,
    record_run: bool = True,
) -> Dict[str, Any]:
    cases = load_eval_baskets()
    if basket_ids:
        allowed = set(basket_ids)
        cases = [c for c in cases if c.id in allowed]
    if not cases:
        raise ValueError("No evaluation baskets matched the filter")

    insight_count = db.query(Insight).count()
    if insight_count == 0:
        raise ValueError("No insights in database — run analysis before MVP evaluation")

    run: Optional[Run] = None
    if record_run:
        run = Run(phase="mvp_eval", status="running")
        db.add(run)
        db.commit()
        db.refresh(run)

    results: List[EvalCaseResult] = []
    for case in cases:
        results.append(_score_case(db, case, limit=limit))

    n = len(results)
    category_hits = sum(1 for r in results if r.category_relevant)
    insight_cited = sum(1 for r in results if r.insight_cited)
    non_rejected = sum(1 for r in results if r.insight_non_rejected)
    passed = sum(1 for r in results if r.passed)

    summary = EvalSummary(
        total_cases=n,
        passed_cases=passed,
        pass_rate=round(passed / n, 3),
        category_hit_rate=round(category_hits / n, 3),
        insight_citation_rate=round(insight_cited / n, 3),
        non_rejected_insight_rate=round(non_rejected / n, 3),
    )

    payload: Dict[str, Any] = {
        "summary": summary,
        "results": results,
        "run_id": run.id if run else None,
    }

    if run:
        run.status = "completed"
        run.finished_at = datetime.now(timezone.utc)
        run.stats_json = {
            "total_cases": n,
            "passed_cases": passed,
            "pass_rate": summary.pass_rate,
            "category_hit_rate": summary.category_hit_rate,
        }
        db.commit()

    return payload
