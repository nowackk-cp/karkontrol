from datetime import date
from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction

from apps.orders.models import FinancialLine, OrderLine
from apps.reports.services import check_report_bounds, recalculate_order
from apps.stores.models import Store

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def store(django_user_model):
    return Store.objects.create(
        owner=django_user_model.objects.create_user("constraint-owner"), name="Constraints"
    )


def create_line(store, **changes):
    data = {
        "store": store,
        "order_number": "limits",
        "line_number": 1,
        "order_date": date(2026, 9, 1),
        "product_name": "Synthetic",
        "sku": "SKU",
        "quantity": 1,
        "unit_price_gross": Decimal("600"),
        "unit_cost_net": Decimal("250"),
        "vat_percent": Decimal("20"),
        "commission_percent": Decimal("20"),
    }
    return OrderLine.objects.create(**(data | changes))


@pytest.mark.parametrize(
    "changes",
    [
        {"desi": Decimal("-1")},
        {"weight_kg": Decimal("-1")},
        {"cost_vat_percent": Decimal("101")},
        {"exchange_rate": Decimal("0")},
        {"currency": "GBP"},
        {"currency": "TRY", "exchange_rate": Decimal("2")},
    ],
)
def test_database_rejects_bypassed_form_validation(store, changes):
    with pytest.raises(IntegrityError), transaction.atomic():
        create_line(store, **changes)


def test_sql_absolute_sum_guard_includes_negative_amounts(store):
    create_line(store)
    create_line(store, line_number=2)
    recalculate_order(store, "limits")
    rows = list(FinancialLine.objects.filter(line__store=store))
    rows[0].profit = 5_000_000_000_000_000_000
    rows[1].profit = -5_000_000_000_000_000_000
    FinancialLine.objects.bulk_update(rows, ["profit"])
    with pytest.raises(ValueError, match="SQL raporlama"):
        check_report_bounds(store)
