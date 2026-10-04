import hashlib
import json
from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.assistant import judge
from apps.assistant.llm import ModelUnavailable
from qa.acceptance import calibrate

pytestmark = pytest.mark.eval


def calibration_rows(count=30):
    return [
        {
            "id": f"J-{index + 1:02}",
            "answer": f"Benzersiz sentetik test cevabı {index + 1}",
            "answer_sha256": hashlib.sha256(
                f"Benzersiz sentetik test cevabı {index + 1}".encode()
            ).hexdigest(),
            "human_pass": index % 2 == 0,
            "judge_pass": index % 2 == 0,
            "reviewer": "synthetic test reviewer",
            "reviewed_at": date.today().isoformat(),
            "human_reason": "synthetic test reason",
        }
        for index in range(count)
    ]


def test_calibration_requires_at_least_30_unique_answers():
    with pytest.raises(ValueError, match="30"):
        calibrate(calibration_rows(20))


def test_calibration_measures_agreement_and_cohen_kappa():
    rows = calibration_rows()
    rows[0]["judge_pass"] = False
    rows[1]["judge_pass"] = True
    result = calibrate(rows)
    assert result["count"] == result["unique_answers"] == 30
    assert result["agreement_percent"] == pytest.approx(100 * 28 / 30)
    assert result["cohen_kappa"] == pytest.approx(13 / 15)
    assert result["disagreements"] == ["J-01", "J-02"]
    assert result["passed"] is True


def test_duplicate_answer_text_is_not_30_independent_answers():
    rows = calibration_rows()
    rows[1]["answer"] = rows[0]["answer"]
    rows[1]["answer_sha256"] = rows[0]["answer_sha256"]
    with pytest.raises(ValueError, match="unique"):
        calibrate(rows)


def test_constant_judge_cannot_claim_useful_calibration():
    rows = calibration_rows()
    for index, record in enumerate(rows):
        record["human_pass"] = index < 29
        record["judge_pass"] = True
    result = calibrate(rows)
    assert result["agreement_percent"] == pytest.approx(100 * 29 / 30)
    assert result["cohen_kappa"] == 0
    assert result["degenerate"] is True
    assert result["passed"] is False


def test_judge_rejects_same_model_before_call(monkeypatch):
    monkeypatch.setenv("KARKONTROL_LLM_MODEL", "same-model")
    monkeypatch.setenv("KARKONTROL_JUDGE_MODEL", "same-model")
    monkeypatch.setenv("KARKONTROL_JUDGE_URL", "http://127.0.0.1:8082")
    monkeypatch.setattr(judge, "local_completion", lambda **kw: pytest.fail("Same model called"))
    with pytest.raises(ModelUnavailable, match="farklı"):
        judge.grade(question="stopaj", answer="Yanıt", source="Kaynak")


def test_prepare_creates_unique_drafts_and_hides_judge_labels(monkeypatch, tmp_path):
    from apps.assistant.management.commands import evaluate_judge

    monkeypatch.setattr(evaluate_judge, "grade", lambda **kwargs: {"judge_pass": True})
    output = tmp_path / "prepared.json"
    blind = tmp_path / "blind.json"
    call_command("evaluate_judge", output=output, blind_output=blind, stdout=StringIO())
    report = json.loads(output.read_text(encoding="utf-8"))
    review = json.loads(blind.read_text(encoding="utf-8"))
    assert len({record["answer_sha256"] for record in report["cases"]}) == 30
    assert report["status"] == "draft_pending_human_selection_and_review"
    assert all(record["human_pass"] is None for record in report["cases"])
    assert all(record["judge_pass"] is None for record in report["cases"])
    assert all("judge_pass" not in record and "reason" not in record for record in review["cases"])


def test_separate_judge_endpoint_and_model_are_passed_to_adapter(monkeypatch):
    monkeypatch.setenv("KARKONTROL_LLM_MODEL", "test-assistant")
    monkeypatch.setenv("KARKONTROL_JUDGE_MODEL", "test-judge")
    monkeypatch.setenv("KARKONTROL_JUDGE_URL", "http://127.0.0.1:8082")

    def complete(**kwargs):
        assert kwargs["base_url"] == "http://127.0.0.1:8082"
        assert kwargs["model"] == "test-judge"
        return {"grounded": True, "answers_question": True, "clear": True, "reason": "Test"}, {}

    monkeypatch.setattr(judge, "local_completion", complete)
    result = judge.grade(question="Test", answer="Test", source="Test")
    assert result["judge_model"] == "test-judge"
    assert result["judge_pass"] is True


def test_missing_separate_judge_configuration_does_not_call_adapter(monkeypatch):
    monkeypatch.delenv("KARKONTROL_JUDGE_MODEL", raising=False)
    monkeypatch.delenv("KARKONTROL_JUDGE_URL", raising=False)
    monkeypatch.setattr(judge, "local_completion", lambda **kw: pytest.fail("Unconfigured call"))
    with pytest.raises(ModelUnavailable, match="gerekli"):
        judge.grade(question="Test", answer="Test", source="Test")


@pytest.mark.parametrize("change", ["answer", "reason", "reviewer", "date"])
def test_calibration_rejects_changed_sha_or_missing_human_evidence(change):
    rows = calibration_rows()
    if change == "answer":
        rows[0]["answer"] += " changed"
    elif change == "reason":
        rows[0]["human_reason"] = ""
    elif change == "reviewer":
        rows[0]["reviewer"] = "Codex"
    else:
        rows[0]["reviewed_at"] = "2999-01-01"
    with pytest.raises(ValueError):
        calibrate(rows)


def test_all_identical_labels_have_undefined_kappa_and_no_calibration():
    rows = calibration_rows()
    for record in rows:
        record["human_pass"] = record["judge_pass"] = True
    result = calibrate(rows)
    assert result["agreement_percent"] == 100
    assert result["cohen_kappa"] is None
    assert result["degenerate"] is True
    assert result["passed"] is False


def prepared_reports(tmp_path):
    output = tmp_path / "prepared.json"
    blind = tmp_path / "blind.json"
    call_command("evaluate_judge", output=output, blind_output=blind, stdout=StringIO())
    return output, blind


def test_scoring_preserves_blank_human_labels_and_blind_file(monkeypatch, tmp_path):
    from apps.assistant.management.commands import evaluate_judge

    prepared, blind = prepared_reports(tmp_path)
    blind_bytes = blind.read_bytes()
    scores = tmp_path / "scores.json"
    monkeypatch.setattr(
        evaluate_judge,
        "judge_configuration",
        lambda: {"assistant_model": "test-assistant", "judge_model": "test-judge"},
    )
    calls = []

    def grade(**kwargs):
        calls.append(kwargs)
        return {"judge_pass": True, "reason": "synthetic test judgment"}

    monkeypatch.setattr(evaluate_judge, "grade", grade)
    call_command("evaluate_judge", score=prepared, output=scores, stdout=StringIO())
    report = json.loads(scores.read_text(encoding="utf-8"))
    assert len(calls) == 30
    assert report["same_model_as_assistant"] is False
    assert report["human_agreement_percent"] is None
    assert all(record["human_pass"] is None for record in report["cases"])
    assert blind.read_bytes() == blind_bytes
    with pytest.raises(CommandError, match="Output already exists"):
        call_command("evaluate_judge", score=prepared, output=scores, stdout=StringIO())
    assert len(calls) == 30


def test_calibration_joins_blind_human_review_with_independent_scores(tmp_path):
    prepared, blind = prepared_reports(tmp_path)
    report = json.loads(prepared.read_text(encoding="utf-8"))
    review = json.loads(blind.read_text(encoding="utf-8"))
    for index, record in enumerate(review["cases"]):
        record.update(
            human_pass=index % 2 == 0,
            human_reason="synthetic unit fixture",
            reviewer="synthetic unit reviewer",
            reviewed_at=date.today().isoformat(),
        )
        report["cases"][index]["judge_pass"] = index % 2 == 0
    report.update(
        same_model_as_assistant=False, assistant_model="test-assistant", judge_model="test-judge"
    )
    scores = tmp_path / "scores.json"
    scores.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
    blind.write_text(json.dumps(review, ensure_ascii=False), encoding="utf-8")
    output = StringIO()
    call_command("evaluate_judge", human_review=blind, judge_scores=scores, stdout=output)
    result = json.loads(output.getvalue())
    assert result["count"] == result["unique_answers"] == 30
    assert result["agreement_percent"] == 100
    assert result["cohen_kappa"] == 1
    assert result["passed"] is True
    review["cases"][0]["source"] += " tampered"
    blind.write_text(json.dumps(review, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(CommandError, match="content changed"):
        call_command("evaluate_judge", human_review=blind, judge_scores=scores, stdout=StringIO())
