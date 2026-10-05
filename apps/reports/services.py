from decimal import Decimal

from django.db import connection

from apps.orders.models import OrderLine
from apps.orders.search import normalize_search
from apps.orders.services import AMOUNTS as AMOUNTS
from apps.orders.services import check_report_bounds as check_report_bounds
from apps.orders.services import recalculate_order as recalculate_order


def filtered_lines(store, data):
    query = OrderLine.objects.filter(store=store).select_related("financial")
    if data.get("start"):
        query = query.filter(order_date__gte=data["start"])
    if data.get("end"):
        query = query.filter(order_date__lte=data["end"])
    if data.get("product"):
        query = query.filter(search_text__contains=normalize_search(data["product"]))
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
