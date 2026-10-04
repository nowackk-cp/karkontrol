from dataclasses import fields
from decimal import Decimal

from django.db import connection

from apps.orders.models import FinancialLine, OrderLine
from engine.profit import VERSION, LineInput, LineResult, calculate_order

AMOUNTS = tuple(field.name for field in fields(LineResult) if field.name != "line_number")


def recalculate_order(store, order_number, *, enforce_totals=True):
    lines = list(
        OrderLine.objects.filter(store=store, order_number=order_number).order_by("line_number")
    )
    inputs = [
        LineInput(**{field.name: getattr(line, field.name) for field in fields(LineInput)})
        for line in lines
    ]
    results = calculate_order(inputs, marketplace=store.marketplace)
    for line, result in zip(lines, results, strict=True):
        cents = {name: int(getattr(result, name) * 100) for name in AMOUNTS}
        if any(abs(value) > 9_000_000_000_000_000 for value in cents.values()):
            raise ValueError("Hesap tutarı güvenli raporlama sınırını aşıyor.")
        FinancialLine.objects.update_or_create(
            line=line,
            defaults=cents | {"rule_version": VERSION},
        )
    if enforce_totals:
        check_report_bounds(store)


def check_report_bounds(store):
    # Bound the sum of absolute cents, including opposite signs. SQL SUM cannot
    # overflow on any filtered subset or on a cumulative monthly window.
    totals = [0] * len(AMOUNTS)
    for row in FinancialLine.objects.filter(line__store=store).values_list(*AMOUNTS):
        totals = [total + abs(value) for total, value in zip(totals, row, strict=True)]
        if any(total > 9_000_000_000_000_000_000 for total in totals):
            raise ValueError("Mağaza toplamı güvenli SQL raporlama sınırını aşıyor.")


def filtered_lines(store, data):
    from django.db.models import Q

    query = OrderLine.objects.filter(store=store).select_related("financial")
    if data.get("start"):
        query = query.filter(order_date__gte=data["start"])
    if data.get("end"):
        query = query.filter(order_date__lte=data["end"])
    if data.get("product"):
        query = query.filter(
            Q(product_name__icontains=data["product"]) | Q(sku__icontains=data["product"])
        )
    return query


def summary(lines):
    rows = list(lines)
    total = {name: 0 for name in AMOUNTS}
    for line in rows:
        if not hasattr(line, "financial"):
            raise ValueError("Hesap kaydı eksik; rebuild_reports komutunu çalıştırın.")
        for name in AMOUNTS:
            total[name] += getattr(line.financial, name)
    return total


def monthly_sql(store_pk):
    """SQLite kuruş raporu: ay, kâr, hakediş ve birikimli kâr (window function)."""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            WITH monthly AS (
                SELECT substr(o.order_date, 1, 7) AS month,
                       SUM(f.profit) AS profit, SUM(f.payout) AS payout, COUNT(*) AS lines
                FROM orders_orderline o JOIN orders_financialline f ON f.line_id = o.id
                WHERE o.store_id = %s
                GROUP BY substr(o.order_date, 1, 7)
            )
            SELECT month, profit, payout, lines,
                   SUM(profit) OVER (ORDER BY month ROWS UNBOUNDED PRECEDING) AS cumulative
            FROM monthly ORDER BY month
        """,
            [store_pk],
        )
        return [
            dict(zip(("month", "profit", "payout", "lines", "cumulative"), row, strict=True))
            for row in cursor.fetchall()
        ]


def amount(cents):
    return Decimal(cents) / Decimal("100")
