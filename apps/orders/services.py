"""Application services shared by imports, returns and report maintenance."""

from dataclasses import fields

from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.stores.models import Store
from engine.profit import VERSION, LineInput, LineResult, calculate_order

from .models import FinancialLine, ImportBatch, OrderLine

AMOUNTS = tuple(field.name for field in fields(LineResult) if field.name != "line_number")


def rule_version(store):
    return "amazon-demo-v2" if store.marketplace == Store.Marketplace.AMAZON else VERSION


def recalculate_order(store, order_number, *, enforce_totals=True):
    lines = list(
        OrderLine.objects.filter(store=store, order_number=order_number).order_by("line_number")
    )
    if not lines:
        return
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
            defaults=cents | {"rule_version": rule_version(store)},
        )
    if enforce_totals:
        check_report_bounds(store)


def check_report_bounds(store):
    # Absolute sums bound any filtered subset and cumulative monthly window.
    totals = [0] * len(AMOUNTS)
    for row in FinancialLine.objects.filter(line__store=store).values_list(*AMOUNTS):
        totals = [total + abs(value) for total, value in zip(totals, row, strict=True)]
        if any(total > 9_000_000_000_000_000_000 for total in totals):
            raise ValueError("Mağaza toplamı güvenli SQL raporlama sınırını aşıyor.")


@transaction.atomic
def undo_import(*, user, store_pk, batch_pk):
    store = get_object_or_404(Store.objects.select_for_update(), pk=store_pk, owner=user)
    batch = get_object_or_404(ImportBatch.objects.select_for_update(), pk=batch_pk, store=store)
    numbers = list(batch.lines.values_list("order_number", flat=True).distinct())
    deleted_count = batch.lines.count()
    batch.lines.all().delete()
    for number in numbers:
        recalculate_order(store, number, enforce_totals=False)
    check_report_bounds(store)
    batch.delete()
    return deleted_count
