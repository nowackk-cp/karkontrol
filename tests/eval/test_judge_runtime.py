"""Synthetic judge protocol/persistence tests; these do not measure model quality."""

import hashlib
import json
from io import StringIO
from urllib import request

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.assistant import judge
from apps.assistant.llm import ModelUnavailable
from apps.assistant.management.commands import evaluate_judge

pytestmark = pytest.mark.eval


@pytest.fixture(autouse=True)
def synthetic_judge_configuration(monkeypatch):
    monkeypatch.setenv("KARKONTROL_LLM_MODEL", "synthetic-assistant")
    monkeypatch.setenv("KARKONTROL_JUDGE_MODEL", "synthetic-distinct-judge")
    monkeypatch.setenv("KARKONTROL_JUDGE_URL", "http://127.0.0.1:8082")
    monkeypatch.setattr(request, "urlopen", lambda *a, **kw: pytest.fail("Real HTTP forbidden"))


def rubric_response(**changes):
    return {
        "grounded": True,
        "answers_question": True,
        "clear": False,
        "reason": "Synthetic protocol fixture",
        **changes,
    }


def test_decoder_schema_has_no_reason_length_grammar_and_keeps_protocol(monkeypatch):
    calls = []

    def completion(**kwargs):
        calls.append(kwargs)
        return rubric_response(), {"total_tokens": 7}

    monkeypatch.setattr(judge, "local_completion", completion)
    result = judge.grade(question="Synthetic question", answer="Synthetic answer", source="Source")
    assert len(calls) == 1
    assert calls[0]["schema"]["properties"]["reason"] == {"type": "string"}
    assert calls[0]["schema"]["required"] == ["grounded", "answers_question", "clear", "reason"]
    assert calls[0]["schema"]["additionalProperties"] is False
    assert all(
        calls[0]["schema"]["properties"][field] == {"type": "boolean"}
        for field in ("grounded", "answers_question", "clear")
    )
    assert calls[0]["max_tokens"] == 256
    assert calls[0]["model"] == "synthetic-distinct-judge"
    assert calls[0]["base_url"] == "http://127.0.0.1:8082"
    assert calls[0]["messages"][1] == {
        "role": "user",
        "content": "Soru: Synthetic question\nKaynak: Source\nAday yanıt: Synthetic answer",
    }
    assert result["rubric_version"] == "grounding-v1"
    assert result["judge_pass"] is False
    assert result["usage"] == {"total_tokens": 7}


@pytest.mark.parametrize("reason", ["", "ü" * 300])
def test_python_reason_boundary_still_accepts_at_most_300_characters(monkeypatch, reason):
    monkeypatch.setattr(
        judge, "local_completion", lambda **kw: (rubric_response(reason=reason), {})
    )
    assert judge.grade(question="Q", answer="A", source="S")["reason"] == reason


@pytest.mark.parametrize("reason", ["ü" * 301, None, True, 1, []])
def test_python_reason_postvalidation_rejects_long_and_nonstring_reason(monkeypatch, reason):
    monkeypatch.setattr(
        judge, "local_completion", lambda **kw: (rubric_response(reason=reason), {})
    )
    with pytest.raises(ModelUnavailable, match="doğrulanamadı"):
        judge.grade(question="Q", answer="A", source="S")


@pytest.mark.parametrize("field", ["grounded", "answers_question", "clear"])
@pytest.mark.parametrize("invalid", [0, "true", None])
def test_python_rubric_requires_actual_boolean_values(monkeypatch, field, invalid):
    monkeypatch.setattr(
        judge, "local_completion", lambda **kw: (rubric_response(**{field: invalid}), {})
    )
    with pytest.raises(ModelUnavailable, match="doğrulanamadı"):
        judge.grade(question="Q", answer="A", source="S")


@pytest.mark.parametrize("missing", ["grounded", "answers_question", "clear", "reason"])
def test_python_rubric_requires_every_dimension(monkeypatch, missing):
    response = rubric_response()
    del response[missing]
    monkeypatch.setattr(judge, "local_completion", lambda **kw: (response, {}))
    with pytest.raises(ModelUnavailable, match="doğrulanamadı"):
        judge.grade(question="Q", answer="A", source="S")


@pytest.mark.parametrize(
    "response",
    [
        None,
        [],
        "bad",
        ["grounded", "answers_question", "clear", "reason"],
        rubric_response(extra=True),
    ],
)
def test_python_rubric_rejects_malformed_object_and_extra_fields(monkeypatch, response):
    monkeypatch.setattr(judge, "local_completion", lambda **kw: (response, {}))
    with pytest.raises(ModelUnavailable, match="doğrulanamadı"):
        judge.grade(question="Q", answer="A", source="S")


def synthetic_candidates(tmp_path, count=30):
    rows = []
    for index in range(count):
        answer = f"Synthetic persistence fixture {index + 1}"
        rows.append(
            {
                "id": f"SYNTHETIC-{index + 1:02}",
                "question": f"Synthetic question {index + 1}",
                "answer": answer,
                "source": "Synthetic source",
                "answer_sha256": hashlib.sha256(answer.encode()).hexdigest(),
                "human_pass": None,
                "human_reason": "",
                "reviewer": "",
                "reviewed_at": "",
            }
        )
    path = tmp_path / "candidates.json"
    path.write_text(
        json.dumps({"sample_origin": "Synthetic persistence fixtures", "cases": rows}),
        encoding="utf-8",
    )
    return path, rows


def partial_rows(output):
    return [
        json.loads(line)
        for line in output.with_suffix(".partial.jsonl").read_text(encoding="utf-8").splitlines()
    ]


@pytest.mark.parametrize("unavailable", [False, True])
def test_second_call_interruption_keeps_first_flushed_raw_result(
    monkeypatch, tmp_path, unavailable
):
    candidates, rows = synthetic_candidates(tmp_path)
    candidate_bytes = candidates.read_bytes()
    output = tmp_path / "scores.json"
    result = {**rubric_response(), "judge_pass": False, "usage": {"total_tokens": 7}}
    calls = []

    def grade(**kwargs):
        calls.append(kwargs)
        if len(calls) == 2:
            assert len(partial_rows(output)) == 1  # Already visible before interrupt/close.
            raise KeyboardInterrupt("Synthetic interruption")
        if unavailable:
            raise ModelUnavailable("Synthetic unavailable")
        return result

    monkeypatch.setattr(evaluate_judge, "grade", grade)
    with pytest.raises(KeyboardInterrupt, match="Synthetic interruption"):
        call_command("evaluate_judge", score=candidates, output=output, stdout=StringIO())
    assert len(calls) == 2
    assert not output.exists()
    assert candidates.read_bytes() == candidate_bytes
    saved = partial_rows(output)
    assert len(saved) == 1
    assert saved[0]["case_id"] == rows[0]["id"]
    assert saved[0]["status"] == ("unavailable" if unavailable else "scored_uncalibrated")
    assert saved[0]["raw_result"] == (
        {"judge_pass": None, "unavailable": True} if unavailable else result
    )
    assert saved[0]["case"]["human_pass"] is None
    assert saved[0]["case"]["human_reason"] == saved[0]["case"]["reviewer"] == ""
    assert saved[0]["case"]["reviewed_at"] == ""
    assert saved[0]["human_agreement_percent"] is None
    assert saved[0]["assistant_model"] == "synthetic-assistant"
    assert saved[0]["judge_model"] == "synthetic-distinct-judge"


def test_existing_partial_is_preserved_and_no_model_call_starts(monkeypatch, tmp_path):
    candidates, _ = synthetic_candidates(tmp_path)
    output = tmp_path / "scores.json"
    partial = output.with_suffix(".partial.jsonl")
    original = b'{"previous_evidence":true}\n'
    partial.write_bytes(original)
    monkeypatch.setattr(
        evaluate_judge, "grade", lambda **kw: pytest.fail("Prior partial overwritten")
    )
    with pytest.raises(CommandError, match="Partial output already exists"):
        call_command("evaluate_judge", score=candidates, output=output, stdout=StringIO())
    assert partial.read_bytes() == original
    assert not output.exists()


def test_completed_partial_has_all_30_raw_results_and_matches_final_cases(monkeypatch, tmp_path):
    candidates, _ = synthetic_candidates(tmp_path)
    output = tmp_path / "scores.json"
    result = {**rubric_response(), "judge_pass": False}
    monkeypatch.setattr(evaluate_judge, "grade", lambda **kw: result)
    call_command("evaluate_judge", score=candidates, output=output, stdout=StringIO())
    final = json.loads(output.read_text(encoding="utf-8"))
    partial = partial_rows(output)
    assert len(partial) == len(final["cases"]) == 30
    assert [item["case"] for item in partial] == final["cases"]
    assert [item["case_id"] for item in partial] == [row["id"] for row in final["cases"]]
    assert all(item["raw_result"] == result for item in partial)
    assert final["human_agreement_percent"] is None
    assert final["status"] == "scored_uncalibrated"
    final_bytes = output.read_bytes()
    partial_bytes = output.with_suffix(".partial.jsonl").read_bytes()
    with pytest.raises(CommandError, match="Output already exists"):
        call_command("evaluate_judge", score=candidates, output=output, stdout=StringIO())
    assert output.read_bytes() == final_bytes
    assert output.with_suffix(".partial.jsonl").read_bytes() == partial_bytes


def test_final_report_exclusive_create_preserves_a_concurrent_output(monkeypatch, tmp_path):
    output = tmp_path / "concurrent.json"
    previous = '{"previous_evidence":true}'
    original_open = type(output).open

    def open_with_concurrent_create(path, mode="r", *args, **kwargs):
        if path == output and mode == "x":
            output.write_text(previous, encoding="utf-8")
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(type(output), "open", open_with_concurrent_create)
    with pytest.raises(CommandError, match="Output already exists"):
        evaluate_judge.write_report(output, {"new_evidence": True})
    assert output.read_text(encoding="utf-8") == previous


def test_unavailable_calls_keep_null_judge_labels_and_blank_human_evidence(monkeypatch, tmp_path):
    candidates, _ = synthetic_candidates(tmp_path)
    output = tmp_path / "scores.json"

    def unavailable(**kwargs):
        raise ModelUnavailable("Synthetic unavailable")

    monkeypatch.setattr(evaluate_judge, "grade", unavailable)
    with pytest.raises(CommandError, match="Some judge calls unavailable"):
        call_command("evaluate_judge", score=candidates, output=output, stdout=StringIO())
    final = json.loads(output.read_text(encoding="utf-8"))
    partial = partial_rows(output)
    assert len(partial) == len(final["cases"]) == 30
    assert all(row["judge_pass"] is None and row["unavailable"] for row in final["cases"])
    assert all(row["human_pass"] is None and not row["reviewer"] for row in final["cases"])
    assert all(item["status"] == "unavailable" for item in partial)
    assert all(item["raw_result"] == {"judge_pass": None, "unavailable": True} for item in partial)
    assert final["human_agreement_percent"] is None


def test_fewer_than_30_candidates_still_fail_before_partial_or_model_call(monkeypatch, tmp_path):
    candidates, _ = synthetic_candidates(tmp_path, count=29)
    output = tmp_path / "scores.json"
    monkeypatch.setattr(
        evaluate_judge, "grade", lambda **kw: pytest.fail("Insufficient cases called")
    )
    with pytest.raises(CommandError, match="30 distinct"):
        call_command("evaluate_judge", score=candidates, output=output, stdout=StringIO())
    assert not output.exists()
    assert not output.with_suffix(".partial.jsonl").exists()
