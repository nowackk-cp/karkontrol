import csv
from datetime import date
from decimal import Decimal
from io import BytesIO, StringIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.http import Http404
from django.test import override_settings
from django.urls import reverse
from openpyxl import Workbook

from apps.orders import importing
from apps.orders.importing import REQUIRED_COLUMNS, ImportValidationError, import_orders
from apps.orders.models import ImportBatch, OrderLine
from apps.stores.models import Store

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def owner(django_user_model):
    return django_user_model.objects.create_user("sentetik-a", password="test-only-password")


@pytest.fixture
def other(django_user_model):
    return django_user_model.objects.create_user("sentetik-b", password="test-only-password")


@pytest.fixture
def store(owner):
    return Store.objects.create(owner=owner, name="Sentetik A", commission_percent=Decimal("18.00"))


def row(**overrides):
    data = dict(
        zip(
            REQUIRED_COLUMNS,
            ["SIP-001", "1", "01.09.2026", "Türkçe çanta", "SKU-A", "2", "149,99", "20", "50,00"],
            strict=True,
        )
    )
    return data | overrides


def csv_upload(rows, *, name="orders.csv", delimiter=";", columns=None):
    columns = columns or list(dict.fromkeys(key for record in rows for key in record))
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns, delimiter=delimiter)
    writer.writeheader()
    writer.writerows(rows)
    return SimpleUploadedFile(name, ("\ufeff" + stream.getvalue()).encode("utf-8"))


def xlsx_upload(rows, *, extra_sheet=False):
    workbook = Workbook()
    columns = list(rows[0])
    workbook.active.append(columns)
    for record in rows:
        workbook.active.append([record.get(name) for name in columns])
    if extra_sheet:
        workbook.create_sheet("extra")
    stream = BytesIO()
    workbook.save(stream)
    workbook.close()
    return SimpleUploadedFile("orders.xlsx", stream.getvalue())


def load(owner, store, upload):
    return import_orders(user=owner, store_pk=store.pk, upload=upload)


@pytest.mark.parametrize("delimiter", [";", ","])
def test_csv_import_30_lines_preserves_decimal_and_turkish(owner, store, delimiter):
    result = load(
        owner,
        store,
        csv_upload(
            [row(siparis_no=f"SIP-{index:03}") for index in range(1, 31)], delimiter=delimiter
        ),
    )
    assert (result.created, result.skipped) == (30, 0)
    assert OrderLine.objects.count() == 30
    line = OrderLine.objects.get(order_number="SIP-001")
    assert line.unit_price_gross == Decimal("149.99")
    assert isinstance(line.unit_price_gross, Decimal)
    assert line.commission_percent == Decimal("18.00")
    assert line.product_name == "Türkçe çanta"
    assert line.order_date == date(2026, 9, 1)


def test_xlsx_numeric_cells_and_excel_date_preserve_input(owner, store):
    result = load(
        owner,
        store,
        xlsx_upload(
            [row(tarih=date(2026, 9, 2), adet=2, birim_fiyat_kdv_dahil=149.99, kdv_orani=20)]
        ),
    )
    assert result.created == 1
    line = OrderLine.objects.get()
    assert line.unit_price_gross == Decimal("149.99")
    assert line.order_date == date(2026, 9, 2)


def test_same_file_is_idempotent(owner, store):
    load(owner, store, csv_upload([row()]))
    result = load(owner, store, csv_upload([row()], name="renamed.csv"))
    assert (result.created, result.skipped, result.repeated_file) == (0, 1, True)
    assert OrderLine.objects.count() == ImportBatch.objects.count() == 1


def test_same_rows_in_different_format_are_not_duplicated(owner, store):
    load(owner, store, csv_upload([row()]))
    result = load(owner, store, xlsx_upload([row()]))
    assert (result.created, result.skipped) == (0, 1)
    assert OrderLine.objects.count() == 1


def test_conflict_rolls_back_new_rows_and_batch(owner, store):
    load(owner, store, csv_upload([row()]))
    with pytest.raises(ImportValidationError, match="çelişiyor"):
        load(
            owner,
            store,
            csv_upload([row(siparis_no="SIP-NEW"), row(birim_fiyat_kdv_dahil="199,99")]),
        )
    assert list(OrderLine.objects.values_list("order_number", flat=True)) == ["SIP-001"]
    assert ImportBatch.objects.count() == 1


@pytest.mark.parametrize(
    "change",
    [
        {"adet": "0"},
        {"adet": "-1"},
        {"adet": "1.5"},
        {"birim_fiyat_kdv_dahil": "-1"},
        {"birim_fiyat_kdv_dahil": "NaN"},
        {"birim_fiyat_kdv_dahil": "Infinity"},
        {"birim_fiyat_kdv_dahil": "1,234"},
        {"birim_fiyat_kdv_dahil": "1.234,56"},
        {"birim_fiyat_kdv_dahil": "10000000000.00"},
        {"komisyon_orani": "150"},
        {"kdv_orani": "101"},
        {"iade_adet": "3"},
        {"satici_indirimi": "300"},
        {"para_birimi": "USD"},
        {"tarih": "31.02.2026"},
        {"urun_adi": ""},
        {"urun_kodu": "x" * 65},
    ],
)
def test_invalid_last_row_leaves_no_records(owner, store, change):
    with pytest.raises(ImportValidationError, match="Satır 3"):
        load(owner, store, csv_upload([row(siparis_no="SIP-OK"), row(**change)]))
    assert OrderLine.objects.count() == ImportBatch.objects.count() == 0


def test_duplicate_line_in_file_is_rejected(owner, store):
    with pytest.raises(ImportValidationError, match="birden fazla"):
        load(owner, store, csv_upload([row(), row()]))
    assert OrderLine.objects.count() == 0


def test_multiple_lines_of_same_order_are_supported(owner, store):
    assert load(owner, store, csv_upload([row(), row(satir_no="2")])).created == 2


def test_missing_and_duplicate_columns_fail(owner, store):
    incomplete = row()
    del incomplete["adet"]
    with pytest.raises(ImportValidationError, match="Eksik sütunlar: adet"):
        load(owner, store, csv_upload([incomplete]))
    with pytest.raises(ImportValidationError, match="tekrar"):
        load(owner, store, SimpleUploadedFile("a.csv", b"adet;adet\n1;1"))
    assert ImportBatch.objects.count() == 0


def test_empty_rows_are_ignored(owner, store):
    upload = csv_upload([row()])
    upload = SimpleUploadedFile("a.csv", upload.read() + b"\n;;;;;;;;\n")
    assert load(owner, store, upload).created == 1


@pytest.mark.parametrize(
    "content,name", [(b"", "empty.csv"), (b"broken", "bad.xlsx"), (b"x", "bad.xls")]
)
def test_empty_corrupt_and_unsupported_files_fail(owner, store, content, name):
    with pytest.raises(ImportValidationError):
        load(owner, store, SimpleUploadedFile(name, content))
    assert OrderLine.objects.count() == ImportBatch.objects.count() == 0


def test_formulas_and_multiple_sheets_are_rejected(owner, store):
    with pytest.raises(ImportValidationError, match="Formül"):
        load(owner, store, xlsx_upload([row(birim_fiyat_kdv_dahil="=100+20")]))
    with pytest.raises(ImportValidationError, match="tek çalışma"):
        load(owner, store, xlsx_upload([row()], extra_sheet=True))


def test_file_and_row_limits(owner, store, monkeypatch):
    monkeypatch.setattr(importing, "MAX_FILE_BYTES", 8)
    with pytest.raises(ImportValidationError, match="boyutu"):
        load(owner, store, csv_upload([row()]))
    monkeypatch.setattr(importing, "MAX_FILE_BYTES", 5 * 1024 * 1024)
    monkeypatch.setattr(importing, "MAX_ROWS", 1)
    with pytest.raises(ImportValidationError, match="en fazla 1"):
        load(owner, store, csv_upload([row(), row(satir_no="2")]))
    monkeypatch.setattr(importing, "MAX_EXPANDED_BYTES", 1)
    with pytest.raises(ImportValidationError, match="açılmış boyutu"):
        load(owner, store, xlsx_upload([row()]))


def test_import_service_rejects_other_owners_store(owner, other, store):
    with pytest.raises(Http404):
        load(other, store, csv_upload([row()]))
    assert OrderLine.objects.count() == 0


def test_same_order_number_allowed_in_separate_stores(owner, other, store):
    other_store = Store.objects.create(owner=other, name="B")
    load(owner, store, csv_upload([row()]))
    load(other, other_store, csv_upload([row()]))
    assert OrderLine.objects.count() == 2


@pytest.mark.parametrize("route", ["list", "upload", "sample", "return"])
@pytest.mark.parametrize("method", ["get", "post"])
def test_foreign_store_routes_return_404(client, owner, other, store, route, method):
    load(owner, store, csv_upload([row()]))
    client.force_login(other)
    kwargs = {"store_pk": store.pk}
    if route == "return":
        kwargs["pk"] = OrderLine.objects.get().pk
    response = getattr(client, method)(reverse(f"orders:{route}", kwargs=kwargs))
    assert response.status_code == 404
    assert OrderLine.objects.get().returned_quantity == 0


def test_store_creation_ignores_forged_owner_and_validates_commission(client, owner, other):
    client.force_login(owner)
    url = reverse("stores:create")
    data = {
        "name": "Yeni",
        "marketplace": "demo_tr",
        "commission_percent": "150",
        "owner": other.pk,
    }
    assert client.post(url, data).status_code == 200
    assert Store.objects.count() == 0
    data["commission_percent"] = "20.00"
    assert client.post(url, data).status_code == 302
    assert Store.objects.get().owner == owner
    assert client.post(url, data).status_code == 200
    assert Store.objects.count() == 1


def test_store_list_and_anonymous_access(client, owner, other, store):
    Store.objects.create(owner=other, name="Gizli B")
    assert client.get(reverse("stores:list")).status_code == 302
    client.force_login(owner)
    response = client.get(reverse("stores:list"))
    assert b"Sentetik A" in response.content
    assert b"Gizli B" not in response.content


def test_database_constraints_block_duplicate_and_invalid_commission(owner, store):
    with pytest.raises(IntegrityError), transaction.atomic():
        Store.objects.create(owner=owner, name="Invalid", commission_percent=Decimal("150"))
    with pytest.raises(IntegrityError), transaction.atomic():
        Store.objects.create(owner=owner, name=store.name)


def test_upload_view_sample_and_turkish_money_format(client, owner, store):
    client.force_login(owner)
    sample = client.get(reverse("orders:sample", args=[store.pk]))
    assert sample.status_code == 200
    assert "attachment" in sample["Content-Disposition"]
    response = client.post(
        reverse("orders:upload", args=[store.pk]),
        {"file": SimpleUploadedFile("sample.csv", sample.content)},
        follow=True,
    )
    assert response.status_code == 200
    assert "1 sipariş satırı aktarıldı" in response.content.decode()
    assert "149,99 ₺" in response.content.decode()
    invalid = client.post(
        reverse("orders:upload", args=[store.pk]),
        {"file": SimpleUploadedFile("bad.csv", b"wrong\n1")},
    )
    assert invalid.status_code == 200
    assert "Eksik sütunlar" in invalid.content.decode()
    assert OrderLine.objects.count() == 1


def test_filters_are_inclusive_and_invalid_range_shows_no_rows(client, owner, store):
    load(
        owner,
        store,
        csv_upload(
            [
                row(siparis_no="A", tarih="2026-09-01"),
                row(siparis_no="B", tarih="2026-09-30", urun_adi="Fincan", urun_kodu="MATCH"),
                row(siparis_no="C", tarih="2026-10-01"),
            ]
        ),
    )
    client.force_login(owner)
    url = reverse("orders:list", args=[store.pk])
    response = client.get(url, {"start": "2026-09-01", "end": "2026-09-30"})
    assert response.context["filtered_count"] == 2
    assert 'value="2026-09-01"' in response.content.decode()
    assert client.get(url, {"product": "MATCH"}).context["filtered_count"] == 1
    bad = client.get(url, {"start": "2026-10-01", "end": "2026-09-01"})
    assert bad.context["filtered_count"] == 0
    assert bad.context["filter_form"].non_field_errors()


def test_pagination_preserves_filters(client, owner, store):
    load(owner, store, csv_upload([row(siparis_no=f"A-{i}") for i in range(51)]))
    client.force_login(owner)
    response = client.get(
        reverse("orders:list", args=[store.pk]), {"product": "SKU-A", "page": "2"}
    )
    assert response.context["filtered_count"] == 51
    assert len(response.context["lines"]) == 1
    assert response.context["filter_query"] == "product=SKU-A"


def test_return_quantity_validation_and_line_ownership(client, owner, other, store):
    load(owner, store, csv_upload([row()]))
    line = OrderLine.objects.get()
    client.force_login(owner)
    url = reverse("orders:return", args=[store.pk, line.pk])
    assert client.post(url, {"returned_quantity": 3}).status_code == 200
    line.refresh_from_db()
    assert line.returned_quantity == 0
    assert client.post(url, {"returned_quantity": 2}).status_code == 302
    line.refresh_from_db()
    assert line.returned_quantity == 2
    foreign = Store.objects.create(owner=other, name="B")
    load(other, foreign, csv_upload([row()]))
    foreign_line = OrderLine.objects.get(store=foreign)
    assert (
        client.post(
            reverse("orders:return", args=[store.pk, foreign_line.pk]), {"returned_quantity": 1}
        ).status_code
        == 404
    )


def test_demo_seed_is_local_only_idempotent_and_preserves_existing_users(
    django_user_model, monkeypatch
):
    monkeypatch.delenv("KARKONTROL_DEMO_PASSWORD", raising=False)
    with pytest.raises(CommandError, match="yalnızca DEBUG"):
        call_command("seed_demo", stdout=StringIO())
    with override_settings(DEBUG=True):
        call_command("seed_demo", stdout=StringIO())
        call_command("seed_demo", stdout=StringIO())
    assert OrderLine.objects.count() == 2
    user = django_user_model.objects.get(username="demo-satici")
    user.set_password("different-password")
    user.save()
    original_hash = user.password
    with override_settings(DEBUG=True), pytest.raises(CommandError, match="değiştirilmedi"):
        call_command("seed_demo", stdout=StringIO())
    user.refresh_from_db()
    assert user.password == original_hash


@pytest.mark.parametrize("quantity", ["9" * 5000, "2147483648"])
def test_very_long_quantity_returns_validation_error_without_partial_records(
    owner, store, quantity
):
    with pytest.raises(ImportValidationError, match="Satır 3"):
        load(
            owner,
            store,
            csv_upload(
                [
                    row(siparis_no="OK"),
                    row(adet=quantity),
                ]
            ),
        )
    assert OrderLine.objects.count() == ImportBatch.objects.count() == 0


def test_largest_supported_quantity_is_preserved(owner, store):
    assert load(owner, store, csv_upload([row(adet="2147483647")])).created == 1
    assert OrderLine.objects.get().quantity == 2147483647
