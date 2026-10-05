from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST, require_safe

from apps.stores.views import store_owner_required

from .forms import OrderFilterForm, ReturnForm, UploadForm
from .importing import REQUIRED_COLUMNS, ImportValidationError, import_orders
from .models import OrderLine
from .search import normalize_search
from .services import recalculate_order, undo_import


@login_required
@require_safe
@store_owner_required
def order_list(request, store_pk):
    store = request.karkontrol_store
    lines = OrderLine.objects.filter(store=store)
    form = OrderFilterForm(request.GET)
    if form.is_valid():
        data = form.cleaned_data
        if data["start"]:
            lines = lines.filter(order_date__gte=data["start"])
        if data["end"]:
            lines = lines.filter(order_date__lte=data["end"])
        if data["product"]:
            lines = lines.filter(search_text__contains=normalize_search(data["product"]))
    else:
        lines = lines.none()
    paginator = Paginator(lines, 50)
    page = paginator.get_page(request.GET.get("page"))
    query = request.GET.copy()
    query.pop("page", None)
    return render(
        request,
        "orders/list.html",
        {
            "store": store,
            "lines": page,
            "page_obj": page,
            "filter_form": form,
            "filtered_count": paginator.count,
            "filter_query": query.urlencode(),
            "import_batches": store.import_batches.order_by("-created_at", "-pk")[:20],
        },
    )


@login_required
@store_owner_required
@require_http_methods(["GET", "POST"])
def order_upload(request, store_pk):
    store = request.karkontrol_store
    form = UploadForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        try:
            result = import_orders(
                user=request.user, store_pk=store.pk, upload=form.cleaned_data["file"]
            )
        except ImportValidationError as exc:
            form.add_error("file", str(exc))
        else:
            messages.success(
                request,
                f"{result.created} sipariş satırı aktarıldı; "
                f"{result.skipped} mevcut satır atlandı.",
            )
            return redirect("orders:list", store_pk=store.pk)
    return render(request, "orders/upload.html", {"form": form, "store": store})


@login_required
@store_owner_required
@require_http_methods(["GET", "POST"])
def order_return(request, store_pk, pk):
    store = request.karkontrol_store
    line = get_object_or_404(OrderLine, pk=pk, store=store)
    form = ReturnForm(request.POST if request.method == "POST" else None, instance=line)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            form.save()
            recalculate_order(store, line.order_number)
        messages.success(request, "İade adedi güncellendi.")
        return redirect("orders:list", store_pk=store.pk)
    return render(request, "orders/return.html", {"form": form, "line": line, "store": store})


@login_required
@store_owner_required
@require_POST
def import_undo(request, store_pk, batch_pk):
    store = request.karkontrol_store
    try:
        count = undo_import(user=request.user, store_pk=store.pk, batch_pk=batch_pk)
    except ValueError as exc:
        messages.error(request, f"Aktarım geri alınamadı: {exc}")
    else:
        messages.success(request, f"Aktarım geri alındı; {count} sipariş satırı silindi.")
    return redirect("orders:list", store_pk=store.pk)


@login_required
@store_owner_required
@require_safe
def sample_file(request, store_pk):
    header = ";".join(REQUIRED_COLUMNS)
    row = "DEMO-001;1;2026-09-01;Sentetik ürün;DEMO-SKU;2;149,99;20;50,00"
    response = HttpResponse(
        "\ufeff" + header + "\r\n" + row + "\r\n", content_type="text/csv; charset=utf-8"
    )
    response["Content-Disposition"] = 'attachment; filename="ornek_siparisler.csv"'
    return response
