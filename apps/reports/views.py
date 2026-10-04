import csv

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from apps.orders.forms import OrderFilterForm
from apps.orders.services import rule_version
from apps.stores.views import store_owner_required

from .services import AMOUNTS, amount, filtered_lines, monthly_sql, summary


@login_required
@store_owner_required
@require_safe
def profit_report(request, store_pk):
    store = request.karkontrol_store
    form = OrderFilterForm(request.GET)
    data = form.cleaned_data if form.is_valid() else {}
    lines = filtered_lines(store, data)
    if not form.is_valid():
        lines = lines.none()
    missing_count = lines.filter(financial__isnull=True).count()
    ready_lines = lines.filter(financial__isnull=False)
    total = summary(ready_lines)
    page = Paginator(ready_lines, 50).get_page(request.GET.get("page"))
    query = request.GET.copy()
    query.pop("page", None)
    return render(
        request,
        "reports/profit.html",
        {
            "store": store,
            "filter_form": form,
            "lines": page,
            "total": total,
            "filtered_count": ready_lines.count(),
            "missing_count": missing_count,
            "store_missing_count": store.order_lines.filter(financial__isnull=True).count(),
            "rule_version": rule_version(store),
            "filter_query": query.urlencode(),
            "months": monthly_sql(store.pk),
        },
    )


@login_required
@store_owner_required
@require_safe
def export_csv(request, store_pk):
    form = OrderFilterForm(request.GET)
    if not form.is_valid():
        return HttpResponse("Filtre geçersiz.", status=400)
    lines = filtered_lines(request.karkontrol_store, form.cleaned_data)
    if lines.filter(financial__isnull=True).exists():
        return HttpResponse(
            "Hesap kaydı eksik; CSV oluşturulmadı. Hesap kayıtlarını yeniden oluşturun.",
            status=409,
            content_type="text/plain; charset=utf-8",
        )
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="kar_raporu.csv"'
    response.write("\ufeff")
    writer = csv.writer(response, delimiter=";")
    writer.writerow(["siparis_no", "satir_no", "tarih", "urun_kodu", "kurallar", *AMOUNTS])
    for line in lines:
        # Spreadsheet programs must treat untrusted identifiers as text, not formulas.
        def safe_text(value):
            return "'" + value if value.startswith(("=", "+", "-", "@", "\t", "\r")) else value

        writer.writerow(
            [
                safe_text(line.order_number),
                line.line_number,
                line.order_date,
                safe_text(line.sku),
                line.financial.rule_version,
                *(
                    format(amount(getattr(line.financial, name)), ".2f").replace(".", ",")
                    for name in AMOUNTS
                ),
            ]
        )
    return response
