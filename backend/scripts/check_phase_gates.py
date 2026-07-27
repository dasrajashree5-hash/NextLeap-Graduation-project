#!/usr/bin/env python3
"""Print phase gate status; optional CI exit code."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running from backend/ without installing the package.
BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.db.session import SessionLocal
from app.core.implementation_prompts import evaluate_implementation_prompts
from app.services.key_risks import evaluate_key_risks, failing_risk_ids
from app.services.phase_gates import evaluate_phases


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate implementation phase gates")
    parser.add_argument("--through", type=int, default=6, help="Highest phase to evaluate (1-6)")
    parser.add_argument(
        "--risks",
        action="store_true",
        help="Evaluate key risks (implementation plan §9) instead of phase gates",
    )
    parser.add_argument(
        "--prompts",
        action="store_true",
        help="List implementation prompts and checks (implementation plan §10)",
    )
    parser.add_argument(
        "--fail-on-incomplete",
        action="store_true",
        help="Exit 1 if any automated gate through --through is failing",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.prompts:
            report = evaluate_implementation_prompts()
        elif args.risks:
            report = evaluate_key_risks(db)
        else:
            report = evaluate_phases(db, through=args.through)
    finally:
        db.close()

    print(json.dumps(report, indent=2))

    if not args.fail_on_incomplete:
        return 0

    if args.risks:
        return 1 if failing_risk_ids(report) else 0

    if args.prompts:
        return 0 if report.get("complete") else 1

    for phase in report.get("phases", []):
        for gate in phase.get("gates", []):
            if gate.get("manual"):
                continue
            if gate.get("passed") is False:
                return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
