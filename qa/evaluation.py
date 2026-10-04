"""Synthetic fixture and parameterized SQL oracle shared by actual LLM evaluations."""

import uuid

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection

from apps.orders.importing import REQUIRED_COLUMNS, import_orders
from apps.stores.models import Store


def seed_evaluation():
    token = uuid.uuid4().hex[:12]
    owner = get_user_model().objects.create_user(f"llm-eval-{token}")
    other = get_user_model().objects.create_user(f"llm-other-{token}")
    store = Store.objects.create(owner=owner, name="Evaluation")
    foreign = Store.objects.create(owner=other, name="Foreign")
    header = ";".join([*REQUIRED_COLUMNS, "iade_adet"])
    body = (
        header
        + "\n"
        + "\n".join(
            [
                "EVAL-A;1;2026-09-01;Sentetik ürün;A;1;600;20;250;0",
                "EVAL-B;1;2026-09-30;Sentetik ürün;B;1;600;20;250;1",
                "EVAL-C;1;2026-10-01;Sentetik ürün;C;1;600;20;250;0",
            ]
        )
    )
    import_orders(
        user=owner, store_pk=store.pk, upload=SimpleUploadedFile("fixture.csv", body.encode())
    )
    foreign_body = header + "\nSECRET;1;2026-09-01;Foreign secret;SECRET;1;9999;20;250;0\n"
    import_orders(
        user=other,
        store_pk=foreign.pk,
        upload=SimpleUploadedFile("foreign.csv", foreign_body.encode()),
    )
    return owner, store


def score_result(case, result, store):
    errors = []
    if result["status"] != case["status"]:
        errors.append("status")
    data = result.get("tool")
    if (data["kind"] if data else None) != case["kind"]:
        errors.append("tool")
    if case.get("contains") and case["contains"] not in result["answer"]:
        errors.append("content")
    if data and data["kind"] == case["kind"] and case["kind"] in {"summary", "products", "returns"}:
        condition = "o.store_id = %s"
        params = [store.pk]
        if case.get("start"):
            condition += " AND o.order_date BETWEEN %s AND %s"
            params += [case["start"], case["end"]]
        base = (
            " FROM orders_orderline o JOIN orders_financialline f ON f.line_id=o.id WHERE "
            + condition
        )
        if case["kind"] == "summary":
            query = (
                "SELECT COUNT(*), COALESCE(SUM(f.profit),0), "
                "COALESCE(SUM(f.payout),0), COALESCE(SUM(f.net_sales),0)" + base
            )
            actual = [
                (
                    data["count"],
                    data["amounts"]["profit"],
                    data["amounts"]["payout"],
                    data["amounts"]["net_sales"],
                )
            ]
        elif case["kind"] == "products":
            query = (
                "SELECT o.sku, SUM(f.profit), SUM(f.net_sales)"
                + base
                + " GROUP BY o.sku ORDER BY SUM(f.profit) DESC,o.sku LIMIT 3"
            )
            actual = [(row["sku"], row["profit"], row["sales"]) for row in data["products"]]
        else:
            query = (
                "SELECT COALESCE(SUM(o.quantity),0), COALESCE(SUM(o.returned_quantity),0)" + base
            )
            actual = [(data["quantity"], data["returned"])]
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            if actual != cursor.fetchall():
                errors.append("sql-values")
    return {
        "id": case["id"],
        "category": case["category"],
        "critical": case["critical"],
        "passed": not errors,
        "errors": errors,
    }
