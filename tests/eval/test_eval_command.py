import json
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.orders.models import OrderLine
from apps.stores.models import Store

pytestmark = [pytest.mark.eval, pytest.mark.django_db]


def test_offline_command_reports_sql_and_rolls_back(tmp_path, django_user_model):
    before = (Store.objects.count(), OrderLine.objects.count(), django_user_model.objects.count())
    output = tmp_path / "eval.json"
    call_command(
        "evaluate_assistant", backend="offline", versions="v1,v2", output=output, stdout=StringIO()
    )
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["model"] is None
    assert report["versions"]["v2"]["gate"]["accuracy_percent"] == 100
    assert report["versions"]["v2"]["model_requests"] == 0
    assert report["regressions"] == []
    assert before == (
        Store.objects.count(),
        OrderLine.objects.count(),
        django_user_model.objects.count(),
    )


def test_real_eval_failure_keeps_report_and_rolls_back(tmp_path, monkeypatch, django_user_model):
    from apps.assistant.management.commands import evaluate_assistant

    output = tmp_path / "failed.json"
    monkeypatch.setattr(
        evaluate_assistant,
        "ask_llm",
        lambda **kwargs: {"status": "unavailable", "tool": None, "answer": "unavailable"},
    )
    with pytest.raises(CommandError, match="gate failed"):
        call_command(
            "evaluate_assistant", backend="local", versions="v2", output=output, stdout=StringIO()
        )
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["versions"]["v2"]["gate"]["accuracy_percent"] == 0
    assert report["versions"]["v2"]["gate"]["critical_failures"]
    assert not Store.objects.exists()
    assert not django_user_model.objects.exists()
