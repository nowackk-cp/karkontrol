import csv
import importlib
from dataclasses import fields
from decimal import Decimal
from io import StringIO
from types import SimpleNamespace

import pytest
from django.apps import apps
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.http import Http404
from django.test import Client
from django.urls import URLPattern, URLResolver, get_resolver, reverse
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from apps.orders import services
from apps.orders.importing import ImportValidationError, import_orders
from apps.orders.models import FinancialLine, ImportBatch, OrderLine
from apps.orders.services import AMOUNTS, undo_import
from apps.reports.services import monthly_sql, summary
from apps.stores.models import Store
from engine.profit import LineInput, calculate_order
from tests.integration.test_stores_orders import csv_upload, row

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def seller(django_user_model):
    owner = django_user_model.objects.create_user("integrity-owner", password="synthetic-pass")
    other = django_user_model.objects.create_user("integrity-other", password="synthetic-pass")
    store = Store.objects.create(owner=owner, name="Bütünlük kontrolü")
    foreign = Store.objects.create(owner=other, name="Diğer kontrol")
    return owner, other, store, foreign


def load(owner, store, records):
    return import_orders(user=owner, store_pk=store.pk, upload=csv_upload(records))


def snapshot(store):
    return list(
        FinancialLine.objects.filter(line__store=store)
        .order_by("line_id")
        .values("line_id", "rule_version", *AMOUNTS)
    )


def test_wrong_import_can_be_undone_atomically(seller, monkeypatch):
    owner, _, store, _ = seller
    load(owner, store, [row()])
    baseline = snapshot(store)
    load(owner, store, [row(satir_no="2"), row(siparis_no="NEW")])
    second = store.import_batches.latest("pk")
    before_undo = snapshot(store)
    original_recalculate = services.recalculate_order

    def fail_recalculation(*args, **kwargs):
        original_recalculate(*args, **kwargs)
        raise ValueError("sentetik yeniden hesaplama hatası")

    monkeypatch.setattr(services, "recalculate_order", fail_recalculation)
    with pytest.raises(ValueError, match="sentetik yeniden hesaplama"):
        undo_import(user=owner, store_pk=store.pk, batch_pk=second.pk)
    assert OrderLine.objects.filter(store=store).count() == 3
    assert ImportBatch.objects.filter(pk=second.pk).exists()
    assert snapshot(store) == before_undo

    monkeypatch.setattr(services, "recalculate_order", original_recalculate)
    assert undo_import(user=owner, store_pk=store.pk, batch_pk=second.pk) == 2
    assert not ImportBatch.objects.filter(pk=second.pk).exists()
    assert snapshot(store) == baseline
    assert load(owner, store, [row(satir_no="2"), row(siparis_no="NEW")]).created == 2


def test_undo_preserves_overlapping_rows_owned_by_original_batch(client, seller):
    owner, _, store, _ = seller
    load(owner, store, [row()])
    first = store.import_batches.get()
    load(owner, store, [row(), row(siparis_no="NEW")])
    second = store.import_batches.latest("pk")
    assert first.lines.count() == second.lines.count() == 1
    original = snapshot(store)[0]
    client.force_login(owner)
    response = client.post(reverse("orders:undo", args=[store.pk, second.pk]), follow=True)
    assert response.status_code == 200
    assert "Aktarım geri alındı; 1 sipariş satırı silindi" in response.content.decode()
    assert snapshot(store) == [original]
    assert store.order_lines.get().import_batch_id == first.pk
    assert client.get(reverse("orders:undo", args=[store.pk, first.pk])).status_code == 405


def test_repeated_overlapping_file_restores_rows_removed_by_other_batch_undo(seller):
    owner, _, store, _ = seller
    load(owner, store, [row()])
    first = store.import_batches.get()
    overlapping = [row(), row(siparis_no="NEW")]
    load(owner, store, overlapping)
    second = store.import_batches.latest("pk")
    assert undo_import(user=owner, store_pk=store.pk, batch_pk=first.pk) == 1
    assert store.order_lines.count() == 1
    result = load(owner, store, overlapping)
    assert (result.created, result.skipped, result.repeated_file) == (1, 1, False)
    assert store.order_lines.count() == 2
    assert second.lines.count() == 2
    assert undo_import(user=owner, store_pk=store.pk, batch_pk=second.pk) == 2
    assert not store.order_lines.exists()
    assert not FinancialLine.objects.filter(line__store=store).exists()


def test_undo_batch_and_service_enforce_owner(client, seller):
    owner, other, store, foreign = seller
    load(other, foreign, [row()])
    batch = foreign.import_batches.get()
    client.force_login(owner)
    before = snapshot(foreign)
    assert client.post(reverse("orders:undo", args=[foreign.pk, batch.pk])).status_code == 404
    assert client.post(reverse("orders:undo", args=[store.pk, batch.pk])).status_code == 404
    with pytest.raises(Http404):
        undo_import(user=owner, store_pk=foreign.pk, batch_pk=batch.pk)
    assert snapshot(foreign) == before


def test_file_return_change_is_a_conflict_even_after_ui_return(client, seller):
    owner, _, store, _ = seller
    load(owner, store, [row(iade_adet="1")])
    line = store.order_lines.get()
    client.force_login(owner)
    assert (
        client.post(
            reverse("orders:return", args=[store.pk, line.pk]), {"returned_quantity": 2}
        ).status_code
        == 302
    )
    with pytest.raises(ImportValidationError, match="çelişiyor"):
        load(owner, store, [row(iade_adet="0"), row(siparis_no="NEW")])
    line.refresh_from_db()
    assert (line.returned_quantity, line.imported_returned_quantity) == (2, 1)
    assert store.order_lines.count() == 1


def test_legacy_unknown_imported_return_does_not_block_overlap_or_reset_ui_return(seller):
    owner, _, store, _ = seller
    load(owner, store, [row()])
    line = store.order_lines.get()
    OrderLine.objects.filter(pk=line.pk).update(
        import_batch=None, imported_returned_quantity=None, returned_quantity=1
    )
    result = load(owner, store, [row(), row(siparis_no="NEW")])
    assert (result.created, result.skipped) == (1, 1)
    line.refresh_from_db()
    assert line.imported_returned_quantity is None
    assert line.returned_quantity == 1
    with pytest.raises(ImportValidationError, match="çelişiyor"):
        load(owner, store, [row(birim_fiyat_kdv_dahil="159,99")])


def store_routes(patterns, namespaces=(), converters=None):
    for pattern in patterns:
        route_converters = (converters or {}) | pattern.pattern.converters
        if isinstance(pattern, URLResolver):
            next_namespaces = namespaces + ((pattern.namespace,) if pattern.namespace else ())
            yield from store_routes(pattern.url_patterns, next_namespaces, route_converters)
        elif isinstance(pattern, URLPattern) and "store_pk" in route_converters and pattern.name:
            yield ":".join((*namespaces, pattern.name)), route_converters


def test_every_store_route_requires_login_and_ownership(client, seller):
    owner, other, _, foreign = seller
    load(other, foreign, [row()])
    foreign_line = foreign.order_lines.get()
    foreign_batch = foreign.import_batches.get()
    routes = list(store_routes(get_resolver().url_patterns))
    assert routes
    for view, converters in routes:
        kwargs = {name: 1 for name in converters}
        kwargs["store_pk"] = foreign.pk
        if "pk" in kwargs:
            kwargs["pk"] = foreign_line.pk
        if "batch_pk" in kwargs:
            kwargs["batch_pk"] = foreign_batch.pk
        url = reverse(view, kwargs=kwargs)
        client.logout()
        for method in ["get", "post"]:
            assert getattr(client, method)(url).status_code == 302, (view, method)
        client.force_login(owner)
        for method in ["get", "post"]:
            assert getattr(client, method)(url).status_code == 404, (view, method)
    assert foreign.order_lines.count() == 1
    assert foreign.import_batches.count() == 1


def test_state_changing_views_require_csrf(seller):
    owner, _, store, _ = seller
    load(owner, store, [row()])
    line = store.order_lines.get()
    batch = store.import_batches.get()
    client = Client(enforce_csrf_checks=True)
    client.force_login(owner)
    routes = [
        ("stores:create", []),
        ("orders:upload", [store.pk]),
        ("orders:return", [store.pk, line.pk]),
        ("orders:undo", [store.pk, batch.pk]),
        ("assistant:chat", [store.pk]),
        ("billing:subscription", []),
        ("signup", []),
        ("login", []),
        ("logout", []),
    ]
    before = snapshot(store)
    for view, args in routes:
        assert client.post(reverse(view, args=args)).status_code == 403, view
    assert snapshot(store) == before
    assert store.import_batches.count() == 1


def test_free_limit_allows_exactly_100_and_counts_all_stores(seller):
    owner, _, store, _ = seller
    second = Store.objects.create(owner=owner, name="İkinci mağaza")
    assert load(owner, store, [row(siparis_no=f"A-{i}") for i in range(60)]).created == 60
    assert load(owner, second, [row(siparis_no=f"B-{i}") for i in range(40)]).created == 40
    before = snapshot(second)
    with pytest.raises(ImportValidationError, match="100 satır"):
        load(owner, second, [row(siparis_no="OVER-LIMIT")])
    assert OrderLine.objects.filter(store__owner=owner).count() == 100
    assert second.import_batches.count() == 1
    assert snapshot(second) == before


def test_cp1254_csv_error_explains_utf8_and_leaves_no_records(seller):
    owner, _, store, _ = seller
    file = csv_upload([row(urun_adi="İnce çizgili çanta")])
    text = file.read().decode("utf-8-sig")
    with pytest.raises(ImportValidationError, match="CSV dosyasını UTF-8 olarak kaydedin"):
        import_orders(
            user=owner,
            store_pk=store.pk,
            upload=SimpleUploadedFile("cp1254.csv", text.encode("cp1254")),
        )
    assert not store.order_lines.exists()
    assert not store.import_batches.exists()


def test_export_totals_equal_report_totals(client, seller):
    owner, _, store, _ = seller
    load(
        owner,
        store,
        [
            row(siparis_no="MATCH-1", urun_adi="İpek", iade_adet="1"),
            row(siparis_no="MATCH-2", urun_adi="İpek", tarih="2026-09-30"),
            row(siparis_no="OUT-DATE", urun_adi="İpek", tarih="2026-10-01"),
            row(siparis_no="OUT-PRODUCT", urun_adi="Çanta"),
        ],
    )
    client.force_login(owner)
    params = {"start": "2026-09-01", "end": "2026-09-30", "product": "ipek"}
    report = client.get(reverse("reports:profit", args=[store.pk]), params)
    export = client.get(reverse("reports:export", args=[store.pk]), params)
    assert report.status_code == export.status_code == 200
    records = list(csv.DictReader(StringIO(export.content.decode("utf-8-sig")), delimiter=";"))
    assert {record["siparis_no"] for record in records} == {"MATCH-1", "MATCH-2"}
    assert len(records) == report.context["filtered_count"] == 2
    for name in AMOUNTS:
        total = sum(Decimal(record[name].replace(",", ".")) for record in records)
        assert total * 100 == report.context["total"][name]


def test_partial_missing_ledger_is_explicit_and_count_matches_visible_rows(client, seller):
    owner, _, store, _ = seller
    load(owner, store, [row(), row(siparis_no="MISSING")])
    present = store.order_lines.get(order_number="SIP-001")
    expected = summary([present])
    FinancialLine.objects.filter(line__order_number="MISSING").delete()
    client.force_login(owner)
    response = client.get(reverse("reports:profit", args=[store.pk]))
    assert response.status_code == 200
    assert response.context["missing_count"] == response.context["filtered_count"] == 1
    assert response.context["total"] == expected
    assert len(response.context["lines"]) == 1
    assert "tam mağaza toplamı değildir" in response.content.decode()
    assert client.get(reverse("reports:export", args=[store.pk])).status_code == 409
    filtered = client.get(reverse("reports:profit", args=[store.pk]), {"product": "SKU-A"})
    assert filtered.context["store_missing_count"] == 1
    assert "aylık toplamlar eksiktir" in filtered.content.decode()


def test_store_deletion_cascades_its_batches_lines_and_ledger(seller):
    owner, _, store, _ = seller
    load(owner, store, [row()])
    store.delete()
    assert not ImportBatch.objects.exists()
    assert not OrderLine.objects.exists()
    assert not FinancialLine.objects.exists()


def test_search_and_import_baseline_backfill_does_not_guess_batch(seller):
    owner, _, store, _ = seller
    load(owner, store, [row(urun_adi="İpek Işık", urun_kodu="İ-I", iade_adet="1")])
    line = store.order_lines.get()
    OrderLine.objects.filter(pk=line.pk).update(
        search_text="", imported_returned_quantity=None, import_batch=None
    )
    migration = importlib.import_module("apps.orders.migrations.0004_import_sources_turkish_search")
    migration.backfill_import_and_search(apps, SimpleNamespace(connection=connection))
    line.refresh_from_db()
    assert line.search_text == "ipek ışık\ni-ı"
    assert line.imported_returned_quantity is None
    assert line.import_batch_id is None
    line.sku = "IŞIK"
    line.save(update_fields=["sku"])
    line.refresh_from_db()
    assert line.search_text == "ipek ışık\nışık"


@pytest.mark.property
@settings(max_examples=25, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    records=st.lists(
        st.tuples(st.integers(1, 12), st.integers(100, 90000), st.integers(0, 50000)),
        min_size=1,
        max_size=8,
    )
)
def test_monthly_sql_equals_summary_and_engine_totals(seller, records):
    # This checks independent aggregation paths, not human golden financial values.
    owner, _, store, _ = seller
    store.order_lines.all().delete()
    store.import_batches.all().delete()
    load(
        owner,
        store,
        [
            row(
                siparis_no=f"PROP-{index}",
                tarih=f"2026-{month:02}-01",
                adet="1",
                birim_fiyat_kdv_dahil=f"{Decimal(price) / 100:.2f}",
                birim_maliyet_kdv_haric=f"{Decimal(cost) / 100:.2f}",
            )
            for index, (month, price, cost) in enumerate(records)
        ],
    )
    engine_months = {}
    for line in store.order_lines.all():
        result = calculate_order(
            [LineInput(**{field.name: getattr(line, field.name) for field in fields(LineInput)})]
        )[0]
        month = line.order_date.strftime("%Y-%m")
        totals = engine_months.setdefault(month, {"profit": 0, "payout": 0, "lines": 0})
        totals["profit"] += int(result.profit * 100)
        totals["payout"] += int(result.payout * 100)
        totals["lines"] += 1
    rows = monthly_sql(store.pk)
    accumulated = 0
    for result in rows:
        expected = engine_months[result["month"]]
        accumulated += expected["profit"]
        assert result == {"month": result["month"], **expected, "cumulative": accumulated}
    totals = summary(store.order_lines.all())
    assert totals["profit"] == sum(record["profit"] for record in rows)
    assert totals["payout"] == sum(record["payout"] for record in rows)
