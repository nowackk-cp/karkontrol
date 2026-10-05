"""Independent evidence gates. Empty evidence is failure, never success or zero."""

import csv
import re
from datetime import date
from decimal import Decimal

FIELDS = ("net_sales", "commission", "shipping", "service", "withholding", "profit", "payout")
MONEY = re.compile(r"-?\d{1,16}(?:\.\d{1,2})?\Z")


def read_review(path, expected_ids):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter=";"))
    by_id = {}
    for row in rows:
        identifier = row.get("id", "")
        if identifier in by_id:
            raise ValueError(f"Duplicate review ID: {identifier}")
        if identifier not in expected_ids:
            raise ValueError(f"Unknown review ID: {identifier}")
        if any(
            not row.get(field, "").strip()
            for field in (*FIELDS, "reviewer", "reviewed_at", "source")
        ):
            raise ValueError(f"{identifier}: human expected values/reviewer/date/source missing")
        if row["reviewer"].casefold().strip() in {"ai", "codex", "claude", "gemini", "chatgpt"}:
            raise ValueError(f"{identifier}: AI is not an independent human reviewer")
        if date.fromisoformat(row["reviewed_at"]) > date.today():
            raise ValueError(f"{identifier}: future review date")
        expected = {}
        for field in FIELDS:
            value = row[field].strip()
            if not MONEY.fullmatch(value):
                raise ValueError(
                    f"{identifier}.{field}: expected a decimal amount with at most 2 digits"
                )
            expected[field] = int(Decimal(value) * 100)
        by_id[identifier] = expected
    if set(by_id) != set(expected_ids):
        raise ValueError("Missing reviewed scenarios")
    return by_id


def reconcile(scenarios, reviewed, calculate):
    discrepancies = []
    for scenario in scenarios:
        identifier = scenario["id"]
        actual = calculate(scenario)
        for field in FIELDS:
            difference = actual[field] - reviewed[identifier][field]
            if difference:
                discrepancies.append(
                    {
                        "id": identifier,
                        "field": field,
                        "expected_cents": reviewed[identifier][field],
                        "actual_cents": actual[field],
                        "difference_cents": difference,
                    }
                )
    return discrepancies


def eval_gate(rows, baseline_percent=100):
    if not rows or len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Empty or duplicate eval cases")
    accuracy = sum(row["passed"] is True for row in rows) * 100 / len(rows)
    critical_failures = [row["id"] for row in rows if row["critical"] and row["passed"] is not True]
    return {
        "count": len(rows),
        "accuracy_percent": accuracy,
        "critical_failures": critical_failures,
        "passed": accuracy >= baseline_percent - 3 and not critical_failures,
    }


def calibrate(rows):
    import hashlib

    if len(rows) < 30 or len({row["id"] for row in rows}) != len(rows):
        raise ValueError("At least 30 distinct calibration answers required")
    answers = set()
    for row in rows:
        answer = row.get("answer")
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError(f"{row['id']}: answer text is missing")
        digest = hashlib.sha256(answer.encode("utf-8")).hexdigest()
        if row.get("answer_sha256") != digest:
            raise ValueError(f"{row['id']}: answer SHA256 changed or is missing")
        normalized = " ".join(answer.split()).casefold()
        if normalized in answers:
            raise ValueError("At least 30 unique answer texts required; duplicate answer found")
        answers.add(normalized)
        if (
            type(row.get("human_pass")) is not bool
            or type(row.get("judge_pass")) is not bool
            or not isinstance(row.get("reviewer"), str)
            or not row["reviewer"].strip()
            or not row.get("reviewed_at")
            or not isinstance(row.get("human_reason"), str)
            or not row["human_reason"].strip()
        ):
            raise ValueError(f"{row['id']}: human scoring is missing")
        if row["reviewer"].casefold().strip() in {"ai", "codex", "claude", "gemini", "chatgpt"}:
            raise ValueError(f"{row['id']}: human reviewer required")
        if date.fromisoformat(row["reviewed_at"]) > date.today():
            raise ValueError(f"{row['id']}: future human review date")
    disagreement = [row["id"] for row in rows if row["human_pass"] != row["judge_pass"]]
    count = len(rows)
    matches = count - len(disagreement)
    human_positive = sum(row["human_pass"] for row in rows)
    judge_positive = sum(row["judge_pass"] for row in rows)
    chance_numerator = human_positive * judge_positive + (count - human_positive) * (
        count - judge_positive
    )
    denominator = count * count - chance_numerator
    kappa = (matches * count - chance_numerator) / denominator if denominator else None
    degenerate = human_positive in (0, count) or judge_positive in (0, count)
    agreement = matches * 100 / count
    return {
        "count": count,
        "unique_answers": len(answers),
        "agreement_percent": agreement,
        "cohen_kappa": kappa,
        "degenerate": degenerate,
        "disagreements": disagreement,
        "passed": agreement >= 85 and not degenerate,
    }
