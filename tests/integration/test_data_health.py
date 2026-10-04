import io
import json
from datetime import date
from decimal import Decimal

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.orders.models import FinancialLine, OrderLine
from apps.orders.services import recalculate_order
from apps.stores.models import Store

pytestmark = [pytest.mark.integration, pytest.mark.django_db]
D = Decimal


@pytest.fixture
def data_lines(django_user_model):
    owner = django_user_model.objects.create_user("health-owner")
    stores = [Store.objects.create(owner=owner, name=name) for name in ("A", "B")]
    lines = []
    for index, store in enumerate(stores, 1):
        order = OrderLine.objects.create(
            store=store,
            order_number=f"HEALTH-{index}",
            line_number=1,
            order_date=date(2026, 9, 1),
            product_name="Sentetik ürün",
            sku=f"HEALTH-{index}",
            quantity=1,
            unit_price_gross=D("600.00"),
            unit_cost_net=D("250.00"),
            vat_percent=D("20"),
            commission_percent=D("20"),
            desi=D("1"),
        )
        recalculate_order(store, order.order_number)
        lines.append(order)
    return stores, lines


def health_report(**options):
    output = io.StringIO()
    call_command("check_data_health", json=True, stdout=output, **options)
    return json.loads(output.getvalue())


def test_data_health_detects_corrupt_ledger_without_modifying_data(data_lines):
    stores, lines = data_lines
    FinancialLine.objects.filter(line=lines[0]).update(commission=-1, profit=48000)
    FinancialLine.objects.filter(line=lines[1]).delete()
    before = list(FinancialLine.objects.values().order_by("pk"))
    report = health_report()
    assert report["checked_lines"] == report["finding_count"] == 2
    assert report["findings"] == [
        {
            "line_id": lines[0].pk,
            "store_id": stores[0].pk,
            "codes": ["negative_fee_or_cost", "profit_margin_above_90_percent"],
        },
        {"line_id": lines[1].pk, "store_id": stores[1].pk, "codes": ["missing_ledger"]},
    ]
    assert list(FinancialLine.objects.values().order_by("pk")) == before


def test_data_health_scopes_store_and_fails_only_when_requested(data_lines):
    stores, lines = data_lines
    assert health_report(store=stores[0].pk) == {
        "checked_lines": 1,
        "finding_count": 0,
        "findings": [],
    }
    FinancialLine.objects.filter(line=lines[0]).update(rule_version="obsolete")
    assert health_report(store=stores[1].pk)["finding_count"] == 0
    output = io.StringIO()
    with pytest.raises(CommandError, match="1 anormallik bulundu"):
        call_command(
            "check_data_health", store=stores[0].pk, json=True, fail_on_findings=True, stdout=output
        )
    assert json.loads(output.getvalue())["findings"][0]["codes"] == ["outdated_rule_version"]
