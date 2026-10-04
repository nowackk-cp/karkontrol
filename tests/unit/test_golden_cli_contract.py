"""CLI gate/report tests with stubs; never manufacture human financial expectations."""

import csv
import json
from datetime import date

import pytest

from qa.acceptance import FIELDS, read_review
from scripts import check_golden

pytestmark = pytest.mark.unit


def inputs_and_id_only_reviews(tmp_path, count, ids=None):
    inputs = tmp_path / "inputs.json"
    inputs.write_text(
        json.dumps({"scenarios": [{"id": f"SIP-{index:02}"} for index in range(1, 41)]}),
        encoding="utf-8",
    )
    review = tmp_path / "review.csv"
    with review.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter=";")
        writer.writerow(["id", *FIELDS, "reviewer", "reviewed_at", "source"])
        for identifier in ids or [f"SIP-{index:02}" for index in range(1, count + 1)]:
            writer.writerow([identifier, *([""] * 10)])
    return inputs, review


@pytest.mark.parametrize(
    "review_count,required,exit_code,complete",
    [(10, 10, 0, False), (40, 40, 0, True), (10, 40, 1, False)],
)
def test_golden_minimum_milestone_is_distinct_from_complete_acceptance(
    tmp_path, monkeypatch, review_count, required, exit_code, complete
):
    inputs, review = inputs_and_id_only_reviews(tmp_path, review_count)
    output = tmp_path / "gate-stub.json"
    # Stub provenance and reconciliation: this tests CLI flow only, not finance or humans.
    monkeypatch.setattr(
        check_golden, "read_review", lambda path, identifiers: dict.fromkeys(identifiers)
    )
    reconciled = []

    def reconcile(scenarios, reviewed, calculate):
        reconciled.extend(scenario["id"] for scenario in scenarios)
        assert set(reviewed) == set(reconciled)
        return []

    monkeypatch.setattr(check_golden, "reconcile", reconcile)
    monkeypatch.setattr(
        check_golden, "calculate", lambda *args: pytest.fail("unexpected calculation")
    )
    monkeypatch.setattr(
        check_golden.sys,
        "argv",
        [
            "check_golden",
            "--inputs",
            str(inputs),
            "--review",
            str(review),
            "--output",
            str(output),
            "--required-count",
            str(required),
        ],
    )
    assert check_golden.main() == exit_code
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["passed"] is (exit_code == 0)
    assert report.get("complete_financial_acceptance", False) is complete
    if exit_code == 0:
        assert report["count"] == review_count
        assert report["target_count"] == 40
        assert len(reconciled) == review_count
    else:
        assert "At least 40 known review scenarios required" in report["missing_evidence"]
        assert not reconciled


def test_first_golden_evidence_cannot_be_overwritten_or_recalculated(tmp_path, monkeypatch):
    monkeypatch.setattr(check_golden, "ROOT", tmp_path)
    protected = tmp_path / "data/evidence/golden-first-run.json"
    protected.parent.mkdir(parents=True)
    original = b"synthetic immutable prior evidence"
    protected.write_bytes(original)
    monkeypatch.setattr(
        check_golden, "calculate", lambda *args: pytest.fail("unexpected calculation")
    )
    monkeypatch.setattr(check_golden.sys, "argv", ["check_golden", "--output", str(protected)])
    with pytest.raises(SystemExit) as error:
        check_golden.main()
    assert error.value.code == 2
    assert protected.read_bytes() == original


def test_unknown_review_id_fails_before_provenance_or_calculation(tmp_path, monkeypatch):
    identifiers = [f"SIP-{index:02}" for index in range(1, 10)] + ["UNKNOWN"]
    inputs, review = inputs_and_id_only_reviews(tmp_path, 10, identifiers)
    output = tmp_path / "unknown.json"
    monkeypatch.setattr(check_golden, "read_review", lambda *args: pytest.fail("unexpected review"))
    monkeypatch.setattr(
        check_golden, "calculate", lambda *args: pytest.fail("unexpected calculation")
    )
    monkeypatch.setattr(
        check_golden.sys,
        "argv",
        [
            "check_golden",
            "--inputs",
            str(inputs),
            "--review",
            str(review),
            "--output",
            str(output),
            "--required-count",
            "10",
        ],
    )
    assert check_golden.main() == 1
    assert "known review scenarios required" in json.loads(output.read_text())["missing_evidence"]


def test_duplicate_review_id_is_rejected_using_existing_plan_anchor(tmp_path):
    # Only the original user supplied 600 TL numbers, in a temporary parser unit fixture.
    review = tmp_path / "duplicate.csv"
    row = {
        "id": "PLAN-600",
        "net_sales": "500.00",
        "commission": "120.00",
        "shipping": "60.00",
        "service": "10.00",
        "withholding": "5.00",
        "profit": "60.00",
        "payout": "367.00",
        "reviewer": "Parser unit fixture",
        "reviewed_at": date.today().isoformat(),
        "source": "User supplied 600 TL anchor; synthetic parser test only",
    }
    with review.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=row, delimiter=";")
        writer.writeheader()
        writer.writerows([row, row])
    with pytest.raises(ValueError, match="Duplicate review ID: PLAN-600"):
        read_review(review, {"PLAN-600"})
