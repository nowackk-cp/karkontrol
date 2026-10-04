"""Fail closed until 40 independent human-reviewed financial expectations exist."""

import argparse
import hashlib
import json
import sys
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.profit import LineInput, calculate_order  # noqa: E402
from qa.acceptance import read_review, reconcile  # noqa: E402


def calculate(scenario):
    values = {
        key: Decimal(value) if isinstance(value, str) and key != "currency" else value
        for key, value in scenario["input"].items()
    }
    output = calculate_order([LineInput(**values)], marketplace=scenario["marketplace"])[0]
    return {key: int(value * 100) for key, value in asdict(output).items() if key != "line_number"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=Path, default=ROOT / "data/draft/inputs.json")
    parser.add_argument("--review", type=Path, default=ROOT / "data/draft/manual_review.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "reports/golden-acceptance.json")
    args = parser.parse_args()
    report = {"passed": False, "provenance": "human evidence required; no engine-derived oracle"}
    try:
        scenarios = json.loads(args.inputs.read_text(encoding="utf-8"))["scenarios"]
        identifiers = {row["id"] for row in scenarios}
        if len(scenarios) != 40 or len(identifiers) != 40:
            raise ValueError("Exactly 40 distinct input scenarios required")
        reviewed = read_review(args.review, identifiers)
        report["discrepancies"] = reconcile(scenarios, reviewed, calculate)
        report["review_sha256"] = hashlib.sha256(args.review.read_bytes()).hexdigest()
        report["inputs_sha256"] = hashlib.sha256(args.inputs.read_bytes()).hexdigest()
        report["passed"] = not report["discrepancies"]
        report["count"] = 40
    except (OSError, ValueError, KeyError) as error:
        report["missing_evidence"] = str(error)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
