import csv
from decimal import Decimal
from io import BytesIO, StringIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from openpyxl import Workbook

from apps.orders.importing import REQUIRED_COLUMNS, ImportValidationError, import_orders
from apps.orders.models import FinancialLine, ImportBatch, OrderLine
from apps.stores.models import Store
from tests.integration.test_stores_orders import csv_upload, row

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def seller(django_user_model):
    user = django_user_model.objects.create_user("import-review", password="synthetic-pass")
    return user, Store.objects.create(owner=user, name="İnceleme mağazası")


def load(seller, records):
    user, store = seller
    return import_orders(user=user, store_pk=store.pk, upload=csv_upload(records))


@pytest.mark.parametrize("column", ["kdv_orani", "komisyon_orani", "maliyet_kdv_orani"])
def test_xlsx_percent_formatted_rates_are_rejected(seller, column):
    user, store = seller
    record = row(**{column: Decimal("0.20")})
    columns = list(record)
    workbook = Workbook()
    workbook.active.append(columns)
    workbook.active.append([record[name] for name in columns])
    workbook.active.cell(2, columns.index(column) + 1).number_format = "0%"
    stream = BytesIO()
    workbook.save(stream)
    workbook.close()
    with pytest.raises(ImportValidationError, match="yüzde biçimi kullanmayın"):
        import_orders(
            user=user,
            store_pk=store.pk,
            upload=SimpleUploadedFile("percent.xlsx", stream.getvalue()),
        )
    assert OrderLine.objects.count() == ImportBatch.objects.count() == 0


@pytest.mark.parametrize("column", ["kdv_orani", "maliyet_kdv_orani"])
@pytest.mark.parametrize("value", ["0.20", "8", "18", "21"])
def test_vat_rate_must_be_allowed_value(seller, column, value):
    with pytest.raises(ImportValidationError, match="0, 1, 10 veya 20"):
        load(seller, [row(**{column: value})])
    assert OrderLine.objects.count() == ImportBatch.objects.count() == 0


@pytest.mark.parametrize("value", ["0", "0.20", "0.99"])
def test_commission_below_one_is_rejected(seller, value):
    with pytest.raises(ImportValidationError, match="Komisyon.*1"):
        load(seller, [row(komisyon_orani=value)])
    assert not OrderLine.objects.exists()


def test_csv_short_row_is_rejected(seller):
    user, store = seller
    columns = [*REQUIRED_COLUMNS, "komisyon_orani"]
    content = ";".join(columns) + "\n" + ";".join(row().values()) + "\n"
    with pytest.raises(ImportValidationError, match="Satır 2.*sütun sayısı"):
        import_orders(
            user=user,
            store_pk=store.pk,
            upload=SimpleUploadedFile("short.csv", content.encode("utf-8")),
        )
    assert not OrderLine.objects.exists()


def test_reimport_after_ui_return_imports_new_orders(client, seller):
    user, store = seller
    load(seller, [row()])
    line = OrderLine.objects.get()
    client.force_login(user)
    response = client.post(
        reverse("orders:return", args=[store.pk, line.pk]), {"returned_quantity": 1}
    )
    assert response.status_code == 302
    result = load(seller, [row(), row(siparis_no="NEW")])
    assert (result.created, result.skipped) == (1, 1)
    line.refresh_from_db()
    assert line.returned_quantity == 1
    assert OrderLine.objects.count() == 2


@pytest.mark.parametrize("name,queries", [("İpek", ["ipek", "İPEK"]), ("Işık", ["ışık", "IŞIK"])])
def test_product_filter_matches_turkish_case_variants(client, seller, name, queries):
    user, store = seller
    load(seller, [row(urun_adi=name), row(siparis_no="OTHER", urun_adi="Çanta")])
    client.force_login(user)
    for view in ["orders:list", "reports:profit"]:
        for query in queries:
            response = client.get(reverse(view, args=[store.pk]), {"product": query})
            assert response.status_code == 200
            assert response.context["filtered_count"] == 1


@pytest.mark.parametrize("view", ["reports:profit", "reports:export"])
def test_report_without_ledger_is_not_500(client, seller, view):
    user, store = seller
    load(seller, [row()])
    FinancialLine.objects.all().delete()
    client.force_login(user)
    response = client.get(reverse(view, args=[store.pk]))
    assert response.status_code == (409 if view == "reports:export" else 200)
    assert "Hesap kaydı eksik" in response.content.decode("utf-8-sig")


def test_export_uses_fixed_two_decimal_turkish_amounts(client, seller):
    user, store = seller
    load(seller, [row(adet="1", birim_fiyat_kdv_dahil="600", birim_maliyet_kdv_haric="250")])
    client.force_login(user)
    response = client.get(reverse("reports:export", args=[store.pk]))
    rows = list(csv.DictReader(StringIO(response.content.decode("utf-8-sig")), delimiter=";"))
    assert rows[0]["profit"] == "60,00"
    assert rows[0]["payout"] == "367,00"


def test_amazon_ledger_records_marketplace_rule_version(client, seller):
    user, _ = seller
    store = Store.objects.create(owner=user, name="Amazon inceleme", marketplace="amazon_demo")
    load((user, store), [row()])
    assert FinancialLine.objects.get().rule_version == "amazon-demo-v2"
    client.force_login(user)
    response = client.get(reverse("reports:profit", args=[store.pk]))
    assert "amazon-demo-v2" in response.content.decode()
    assert "demo-v1" not in response.content.decode()
