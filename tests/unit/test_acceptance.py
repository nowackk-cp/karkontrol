import csv
from datetime import date

import pytest

from qa.acceptance import FIELDS, calibrate, eval_gate, read_review, reconcile

pytestmark = pytest.mark.unit


def write_review(tmp_path, **changes):
    path = tmp_path / "review.csv"
    row = {
        "id": "PLAN-600",
        **dict.fromkeys(FIELDS, "0.00"),
        "reviewer": "plan author",
        "reviewed_at": date.today().isoformat(),
        "source": "User supplied 600 TL example",
        **changes,
    }
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=row, delimiter=";")
        writer.writeheader()
        writer.writerow(row)
    return path


@pytest.mark.parametrize("missing", [*FIELDS, "reviewer", "reviewed_at", "source"])
def test_empty_human_evidence_fails(tmp_path, missing):
    with pytest.raises(ValueError, match="missing"):
        read_review(write_review(tmp_path, **{missing: ""}), {"PLAN-600"})


@pytest.mark.parametrize("amount", ["NaN", "1.001", "1e2", "", "Infinity"])
def test_bad_expected_money_fails(tmp_path, amount):
    with pytest.raises(ValueError):
        read_review(write_review(tmp_path, profit=amount), {"PLAN-600"})


def test_human_zero_is_valid_and_one_cent_discrepancy_is_reported(tmp_path):
    reviewed = read_review(write_review(tmp_path, profit="60.00", payout="367.00"), {"PLAN-600"})
    assert reviewed["PLAN-600"]["net_sales"] == 0
    actual = {**reviewed["PLAN-600"], "profit": 6001}
    differences = reconcile([{"id": "PLAN-600"}], reviewed, lambda scenario: actual)
    assert differences == [
        {
            "id": "PLAN-600",
            "field": "profit",
            "expected_cents": 6000,
            "actual_cents": 6001,
            "difference_cents": 1,
        }
    ]


def test_ai_reviewer_is_not_accepted(tmp_path):
    with pytest.raises(ValueError, match="AI"):
        read_review(write_review(tmp_path, reviewer="Codex"), {"PLAN-600"})


def test_eval_baseline_drop_and_critical_failure():
    rows = [{"id": str(i), "critical": False, "passed": True} for i in range(40)]
    rows[0]["passed"] = False
    assert eval_gate(rows)["passed"]  # 97.5 >= 97 baseline gate
    rows[1]["passed"] = False
    assert not eval_gate(rows)["passed"]
    rows[1]["passed"] = True
    rows[0]["critical"] = True
    assert not eval_gate(rows)["passed"]


def test_judge_cannot_claim_calibration_without_human():
    rows = [{"id": str(i), "judge_pass": True} for i in range(20)]
    with pytest.raises(ValueError, match="missing"):
        calibrate(rows)


def test_judge_eighty_five_percent_threshold():
    rows = [
        {
            "id": str(i),
            "human_pass": True,
            "judge_pass": i >= 3,
            "reviewer": "human",
            "reviewed_at": date.today().isoformat(),
        }
        for i in range(20)
    ]
    assert calibrate(rows) == {
        "agreement_percent": 85,
        "disagreements": ["0", "1", "2"],
        "passed": True,
    }
    rows[3]["judge_pass"] = False
    assert not calibrate(rows)["passed"]
