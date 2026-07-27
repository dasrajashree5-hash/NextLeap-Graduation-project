"""Compare model outputs to hand-labelled golden expectations."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping


def _barrier_jaccard(expected: Iterable[str], actual: Iterable[str]) -> float:
    a, b = set(expected or []), set(actual or [])
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def field_agreement(expected: Mapping[str, Any], actual: Mapping[str, Any]) -> Dict[str, float]:
    """Per-field scores in [0, 1] for golden-set regression."""
    scores: Dict[str, float] = {}
    scores["sentiment"] = 1.0 if expected.get("sentiment") == actual.get("sentiment") else 0.0

    exp_disc = expected.get("discovery") or {}
    act_disc = actual.get("discovery") or {}
    if isinstance(exp_disc, Mapping) and isinstance(act_disc, Mapping):
        exp_flag = exp_disc.get("mentions_non_grocery_category")
        act_flag = act_disc.get("mentions_non_grocery_category")
        if exp_flag is not None and act_flag is not None:
            scores["mentions_non_grocery_category"] = 1.0 if exp_flag == act_flag else 0.0
        scores["discovery_barriers"] = _barrier_jaccard(
            exp_disc.get("discovery_barriers") or [],
            act_disc.get("discovery_barriers") or [],
        )
    else:
        scores["discovery_barriers"] = _barrier_jaccard(
            expected.get("discovery_barriers") or [],
            actual.get("discovery_barriers") or [],
        )

    return scores


def weighted_agreement(
    expected: Mapping[str, Any],
    actual: Mapping[str, Any],
    weights: Mapping[str, float] | None = None,
) -> float:
    weights = weights or {
        "sentiment": 0.35,
        "discovery_barriers": 0.45,
        "mentions_non_grocery_category": 0.20,
    }
    scores = field_agreement(expected, actual)
    total_w = sum(weights.get(k, 0.0) for k in scores)
    if total_w == 0:
        return 0.0
    return sum(scores[k] * weights.get(k, 0.0) for k in scores) / total_w


def batch_agreement(
    rows: List[Mapping[str, Any]],
    *,
    expected_key: str = "expected",
    actual_key: str = "baseline_output",
) -> Dict[str, Any]:
    """Aggregate agreement across golden-set rows."""
    if not rows:
        return {"mean": 0.0, "count": 0, "per_field": {}}

    totals: Dict[str, float] = {}
    means: List[float] = []
    for row in rows:
        expected = row.get(expected_key) or {}
        actual = row.get(actual_key) or {}
        # Flatten discovery flags stored at top level in expected
        if "discovery_barriers" in expected and "discovery" not in expected:
            expected = {
                **expected,
                "discovery": {
                    "discovery_barriers": expected.get("discovery_barriers", []),
                    "mentions_non_grocery_category": expected.get(
                        "mentions_non_grocery_category", False
                    ),
                },
            }
        scores = field_agreement(expected, actual)
        means.append(weighted_agreement(expected, actual))
        for k, v in scores.items():
            totals[k] = totals.get(k, 0.0) + v

    count = len(rows)
    return {
        "mean": round(sum(means) / count, 4),
        "count": count,
        "per_field": {k: round(v / count, 4) for k, v in totals.items()},
    }
