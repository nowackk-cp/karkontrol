from datetime import date

import pytest
from django.utils import timezone

from apps.assistant import llm
from apps.assistant.service import ask

pytestmark = [pytest.mark.eval, pytest.mark.django_db]


@pytest.mark.parametrize(
    "question,year,month",
    [
        ("2000 TL üstü siparişler", None, None),
        ("2000,00 TL üstü siparişler", None, None),
        ("2000 adet ürün", None, None),
        ("bu ayakkabı ürününün kârı", None, None),
        ("hangi aralıkta kârım var?", None, None),
        ("09/2026 net kârım", 2026, 9),
        ("2026-09 hakedişim", 2026, 9),
        ("2026 eylul karim", 2026, 9),
        ("geçen ay kârım", 2026, 9),
        ("bu ay satış özeti", 2026, 10),
    ],
)
def test_date_schema_comes_from_period_not_money_or_substrings(monkeypatch, question, year, month):
    monkeypatch.setattr(timezone, "localdate", lambda: date(2026, 10, 4))

    def complete(**kwargs):
        assert kwargs["schema"]["properties"]["year"] == {"enum": [year]}
        assert kwargs["schema"]["properties"]["month"] == {"enum": [month]}
        return {"action": "summary", "topic": "", "year": year, "month": month}, {}

    monkeypatch.setattr(llm, "local_completion", complete)
    assert llm.select_tool(question)[0]["month"] == month


def test_multiple_months_clarify_before_model(evaluation, monkeypatch):
    owner, store = evaluation
    monkeypatch.setattr(
        llm, "select_tool", lambda *args: pytest.fail("ambiguous period calls model")
    )
    result = llm.ask_llm(user=owner, store_pk=store.pk, question="2026 Eylül ve Ekim kârım")
    assert result["status"] == "clarify"


def test_offline_kargo_is_not_profit_substring(evaluation):
    owner, store = evaluation
    result = ask(user=owner, store_pk=store.pk, question="Kargo fiyatını göster")
    assert result["status"] == "unsupported"


def test_period_and_financial_labels_are_explicit(evaluation, monkeypatch):
    owner, store = evaluation
    monkeypatch.setattr(
        llm,
        "select_tool",
        lambda *args: ({"action": "summary", "topic": "", "year": 2026, "month": 9}, {}),
    )
    result = llm.ask_llm(user=owner, store_pk=store.pk, question="2026 Eylül kârım")
    assert result["answer"] == (
        "Eylül 2026: 2 satır için net kâr -60,00 ₺; hakediş 223,00 ₺; net satış 500,00 ₺."
    )
