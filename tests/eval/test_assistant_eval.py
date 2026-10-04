import json
from collections import Counter
from pathlib import Path

import pytest
from django.db import connection

from apps.assistant import service
from apps.assistant.service import ask, guardrail

CASES = [
    json.loads(line)
    for line in Path(__file__).with_name("questions.jsonl").read_text(encoding="utf-8").splitlines()
]
pytestmark = [pytest.mark.eval, pytest.mark.django_db]


def expected_sql(case, store):
    condition = "o.store_id = %s"
    params = [store.pk]
    if case.get("start"):
        condition += " AND o.order_date BETWEEN %s AND %s"
        params += [case["start"], case["end"]]
    base = (
        "FROM orders_orderline o JOIN orders_financialline f ON f.line_id = o.id WHERE " + condition
    )
    kind = case["kind"]
    if kind == "summary":
        query = "SELECT COUNT(*), COALESCE(SUM(f.profit), 0), COALESCE(SUM(f.payout), 0) " + base
    elif kind == "products":
        query = (
            "SELECT o.sku, SUM(f.profit), SUM(f.net_sales) "
            + base
            + " GROUP BY o.sku ORDER BY SUM(f.profit) DESC, o.sku LIMIT 3"
        )
    else:
        query = "SELECT COALESCE(SUM(o.quantity), 0), COALESCE(SUM(o.returned_quantity), 0) " + base
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_question_against_sql_and_guardrail(evaluation, case):
    owner, store = evaluation
    result = ask(user=owner, store_pk=store.pk, question=case["question"])
    assert result["status"] == case["status"]
    assert (result["tool"]["kind"] if result["tool"] else None) == case["kind"]
    if case.get("contains"):
        assert case["contains"] in result["answer"]
    if result["tool"]:
        assert guardrail(result["answer"], result["allowed_numbers"])
    if case["kind"] in {"summary", "products", "returns"}:
        sql = expected_sql(case, store)
        actual = result["tool"]
        if case["kind"] == "summary":
            assert (
                actual["count"],
                actual["amounts"]["profit"],
                actual["amounts"]["payout"],
            ) == sql[0]
        elif case["kind"] == "products":
            assert [(row["sku"], row["profit"], row["sales"]) for row in actual["products"]] == sql
        else:
            assert (actual["quantity"], actual["returned"]) == sql[0]


def test_eval_inventory():
    assert len(CASES) == len({case["id"] for case in CASES}) == 40
    assert Counter(case["category"] for case in CASES) == {
        "numeric": 12,
        "ranking": 8,
        "rules": 6,
        "no_data": 6,
        "ambiguous": 4,
        "security": 4,
    }
    assert sum(case["split"] == "reserved" for case in CASES) == 10


@pytest.mark.parametrize("question", ["", None, "x" * 1001])
def test_invalid_question(evaluation, question):
    owner, store = evaluation
    assert ask(user=owner, store_pk=store.pk, question=question)["status"] == "clarify"


def test_injected_numeric_answer_is_blocked(evaluation, monkeypatch):
    owner, store = evaluation
    monkeypatch.setattr(service, "_render", lambda data: ("Kâr 999,00 ₺", {"60,00"}))
    assert ask(user=owner, store_pk=store.pk, question="özet")["status"] == "blocked"


def test_unrecognized_rule_topic(evaluation):
    owner, store = evaluation
    assert ask(user=owner, store_pk=store.pk, question="Hava nasıl?")["status"] == "unsupported"
