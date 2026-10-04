import hashlib
import json
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.assistant.management.commands import generate_holdout

pytestmark = pytest.mark.eval


def test_changed_prompt_cannot_generate_holdout(monkeypatch, tmp_path):
    monkeypatch.setattr(
        generate_holdout, "local_completion", lambda **k: pytest.fail("No model call")
    )
    with pytest.raises(CommandError, match="frozen"):
        call_command("generate_holdout", prompt_sha256="changed", output=tmp_path / "cases.jsonl")


def test_generated_questions_are_hidden_and_not_regenerated(monkeypatch, tmp_path):
    monkeypatch.setattr(
        generate_holdout,
        "local_completion",
        lambda **k: ({"question": k["messages"][1]["content"]}, {}),
    )
    prompt_hash = hashlib.sha256((generate_holdout.PROMPTS / "v2.txt").read_bytes()).hexdigest()
    output = tmp_path / "cases.jsonl"
    console = StringIO()
    call_command("generate_holdout", prompt_sha256=prompt_hash, output=output, stdout=console)
    cases = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert len({case["id"] for case in cases}) == 10
    assert all(case["question"] not in console.getvalue() for case in cases)
    manifest = json.loads(output.with_suffix(".manifest.json").read_text())
    assert manifest["human_reviewed"] is False
    assert manifest["questions_sha256"] == hashlib.sha256(output.read_bytes()).hexdigest()
    with pytest.raises(CommandError, match="regenerate"):
        call_command("generate_holdout", prompt_sha256=prompt_hash, output=output)
