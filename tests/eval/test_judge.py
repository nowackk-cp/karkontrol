import json
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.assistant import judge

pytestmark = pytest.mark.eval


def test_judge_requires_all_rubric_dimensions(monkeypatch):
    monkeypatch.setenv("KARKONTROL_JUDGE_MODEL", "distinct-test-judge")
    monkeypatch.setenv("KARKONTROL_JUDGE_URL", "http://127.0.0.1:8082")
    monkeypatch.setattr(
        judge,
        "local_completion",
        lambda **kwargs: (
            {"grounded": False, "answers_question": True, "clear": True, "reason": "Çelişki"},
            {},
        ),
    )
    result = judge.grade(question="stopaj", answer="Yanlış", source="Kaynak")
    assert result["judge_pass"] is False


def test_generated_judge_scores_do_not_fill_human_evidence(monkeypatch, tmp_path):
    from apps.assistant.management.commands import evaluate_judge

    monkeypatch.setattr(evaluate_judge, "grade", lambda **kwargs: {"judge_pass": True})
    path = tmp_path / "judge.json"
    call_command("evaluate_judge", output=path, stdout=StringIO())
    report = json.loads(path.read_text(encoding="utf-8"))
    assert len(report["cases"]) == 30
    assert report["human_agreement_percent"] is None
    assert all(row["human_pass"] is None and not row["reviewer"] for row in report["cases"])
    with pytest.raises(CommandError, match="missing"):
        call_command("evaluate_judge", human_review=path, stdout=StringIO())
