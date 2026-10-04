import csv

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from apps.orders.forms import OrderFilterForm
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
    total = summary(lines)
    page = Paginator(lines, 50).get_page(request.GET.get("page"))
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
            "filtered_count": lines.count(),
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
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="kar_raporu.csv"'
    response.write("\ufeff")
    writer = csv.writer(response, delimiter=";")
    writer.writerow(["siparis_no", "satir_no", "tarih", "urun_kodu", "kurallar", *AMOUNTS])
    for line in filtered_lines(request.karkontrol_store, form.cleaned_data):
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
                *(str(amount(getattr(line.financial, name))) for name in AMOUNTS),
            ]
        )
    return response
