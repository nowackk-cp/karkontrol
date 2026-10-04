import csv
import uuid
from decimal import Decimal
from io import StringIO

import pytest
from django.core.management import call_command
from django.http import Http404
from django.urls import reverse

from apps.assistant.service import ask, guardrail
from apps.billing.models import PaymentAttempt, Subscription
from apps.billing.services import demo_payment
from apps.orders.importing import ImportValidationError, import_orders
from apps.orders.models import FinancialLine, OrderLine
from apps.reports.services import monthly_sql, summary
from apps.reports.templatetags.money import tl
from apps.stores.models import Store
from tests.integration.test_stores_orders import csv_upload, row

pytestmark = [pytest.mark.integration, pytest.mark.django_db]
D = Decimal


@pytest.fixture
def finance(django_user_model):
    owner = django_user_model.objects.create_user("finance-owner", password="synthetic-pass-2026")
    other = django_user_model.objects.create_user("finance-other", password="synthetic-pass-2026")
    store = Store.objects.create(owner=owner, name="Finans demo")
    foreign = Store.objects.create(owner=other, name="Diğer demo")
    input_row = row(adet="1", birim_fiyat_kdv_dahil="600", birim_maliyet_kdv_haric="250")
    import_orders(user=owner, store_pk=store.pk, upload=csv_upload([input_row]))
    import_orders(user=other, store_pk=foreign.pk, upload=csv_upload([input_row]))
    return owner, other, store, foreign


def test_import_persists_cents_and_cash_path(finance):
    _, _, store, _ = finance
    financial = FinancialLine.objects.get(line__store=store)
    assert financial.profit == 6000
    assert financial.payout == 36700
    assert financial.rule_version == "demo-v1"
    assert isinstance(financial.profit, int)


def test_monthly_sql_window_isolation_and_filter_totals(finance):
    owner, _, store, foreign = finance
    for number, day in [("second", "2026-09-30"), ("third", "2026-10-01")]:
        import_orders(
            user=owner,
            store_pk=store.pk,
            upload=csv_upload(
                [
                    row(
                        siparis_no=number,
                        tarih=day,
                        adet="1",
                        birim_fiyat_kdv_dahil="600",
                        birim_maliyet_kdv_haric="250",
                    ),
                ]
            ),
        )
    assert monthly_sql(store.pk) == [
        {"month": "2026-09", "profit": 12000, "payout": 73400, "lines": 2, "cumulative": 12000},
        {"month": "2026-10", "profit": 6000, "payout": 36700, "lines": 1, "cumulative": 18000},
    ]
    assert monthly_sql(foreign.pk)[0]["profit"] == 6000


def test_return_recalculates_whole_order_atomically(client, finance):
    owner, _, store, _ = finance
    client.force_login(owner)
    line = OrderLine.objects.get(store=store)
    response = client.post(
        reverse("orders:return", args=[store.pk, line.pk]), {"returned_quantity": 1}
    )
    assert response.status_code == 302
    line.refresh_from_db()
    assert line.financial.profit == -12000
    assert line.financial.payout == -14400


@pytest.mark.parametrize("view", ["reports:profit", "reports:export", "assistant:chat"])
@pytest.mark.parametrize("method", ["get", "post"])
def test_finance_routes_hide_foreign_store(client, finance, view, method):
    owner, _, _, foreign = finance
    client.force_login(owner)
    assert getattr(client, method)(reverse(view, args=[foreign.pk])).status_code == 404


def test_report_filters_and_csv_formula_protection(client, finance):
    owner, _, store, _ = finance
    client.force_login(owner)
    url = reverse("reports:profit", args=[store.pk])
    response = client.get(url)
    assert response.context["total"]["profit"] == 6000
    assert "60,00 ₺" in response.content.decode()
    assert client.get(url, {"product": "absent"}).context["total"]["profit"] == 0
    assert (
        client.get(url, {"start": "2026-10-01", "end": "2026-09-01"}).context["filtered_count"] == 0
    )
    line = OrderLine.objects.get(store=store)
    line.sku = "=1+1"
    line.save(update_fields=["sku"])
    exported = client.get(reverse("reports:export", args=[store.pk]))
    rows = list(csv.reader(StringIO(exported.content.decode("utf-8-sig")), delimiter=";"))
    assert rows[1][3] == "'=1+1"
    assert rows[1][4] == "demo-v1"
    assert (
        client.get(reverse("reports:export", args=[store.pk]), {"start": "bad"}).status_code == 400
    )


def test_report_pagination_totals_all_rows(client, finance):
    owner, _, store, _ = finance
    Subscription.objects.update_or_create(user=owner, defaults={"plan": "pro"})
    import_orders(
        user=owner,
        store_pk=store.pk,
        upload=csv_upload(
            [
                row(
                    siparis_no=f"P{i}",
                    adet="1",
                    birim_fiyat_kdv_dahil="600",
                    birim_maliyet_kdv_haric="250",
                )
                for i in range(51)
            ]
        ),
    )
    client.force_login(owner)
    response = client.get(reverse("reports:profit", args=[store.pk]), {"page": 2})
    assert response.context["filtered_count"] == 52
    assert len(response.context["lines"]) == 2
    assert response.context["total"]["profit"] == 52 * 6000


@pytest.mark.parametrize(
    "outcome,plan", [("success", "pro"), ("failed", "free"), ("timeout", "free")]
)
def test_demo_payment_idempotent_and_user_bound(finance, outcome, plan):
    owner, other, _, _ = finance
    key = uuid.uuid4()
    first = demo_payment(owner, key, outcome)
    second = demo_payment(owner, key, "success")
    assert first.pk == second.pk
    assert Subscription.objects.get(user=owner).plan == plan
    assert PaymentAttempt.objects.filter(user=owner).count() == 1
    demo_payment(other, key, "failed")
    assert PaymentAttempt.objects.filter(user=other).count() == 1
    assert Subscription.objects.get(user=other).plan == "free"


def test_payment_form_invalid_and_success(client, finance):
    owner, _, _, _ = finance
    client.force_login(owner)
    url = reverse("billing:subscription")
    assert client.get(url).status_code == 200
    invalid = client.post(url, {"key": "not-uuid", "outcome": "success"})
    assert invalid.context["form"].errors
    with pytest.raises(ValueError):
        demo_payment(owner, uuid.uuid4(), "forged")
    response = client.post(url, {"key": str(uuid.uuid4()), "outcome": "success"}, follow=True)
    assert "Demo Pro etkinleştirildi" in response.content.decode()


def test_free_limit_rolls_back_all_data_then_pro_imports(finance):
    owner, _, store, _ = finance
    records = [row(siparis_no=f"LIMIT{i}") for i in range(100)]
    with pytest.raises(ImportValidationError, match="100 satır"):
        import_orders(user=owner, store_pk=store.pk, upload=csv_upload(records))
    assert OrderLine.objects.filter(store=store).count() == 1
    assert store.import_batches.count() == 1
    demo_payment(owner, uuid.uuid4(), "success")
    assert import_orders(user=owner, store_pk=store.pk, upload=csv_upload(records)).created == 100


@pytest.mark.parametrize("currency,rate", [("USD", "40"), ("EUR", "45.123456")])
def test_amazon_import_preserves_fx_and_try_regression(finance, currency, rate):
    owner, _, store, _ = finance
    amazon = Store.objects.create(owner=owner, name=f"Amazon {currency}", marketplace="amazon_demo")
    record = row(adet="1", birim_fiyat_kdv_dahil="10", para_birimi=currency, doviz_kuru=rate)
    import_orders(user=owner, store_pk=amazon.pk, upload=csv_upload([record]))
    line = OrderLine.objects.get(store=amazon)
    assert line.exchange_rate == D(rate)
    assert line.financial.gross_sales == int((D("10") * D(rate)).quantize(D("0.01")) * 100)
    assert line.financial.shipping == 8000
    assert FinancialLine.objects.get(line__store=store).profit == 6000


@pytest.mark.parametrize(
    "currency,rate", [("USD", ""), ("USD", "0"), ("USD", "1.0000001"), ("TRY", "2"), ("EUR", "NaN")]
)
def test_invalid_exchange_rate_rolls_back(finance, currency, rate):
    owner, _, _, _ = finance
    amazon = Store.objects.create(owner=owner, name="FX invalid", marketplace="amazon_demo")
    with pytest.raises(ImportValidationError):
        import_orders(
            user=owner,
            store_pk=amazon.pk,
            upload=csv_upload([row(para_birimi=currency, doviz_kuru=rate)]),
        )
    assert not OrderLine.objects.filter(store=amazon).exists()


def test_missing_ledger_rebuild_and_safe_aggregate_limit(finance):
    owner, _, store, _ = finance
    FinancialLine.objects.filter(line__store=store).delete()
    with pytest.raises(ValueError, match="Hesap kaydı eksik"):
        summary(OrderLine.objects.filter(store=store))
    call_command("rebuild_reports")
    assert summary(OrderLine.objects.filter(store=store))["profit"] == 6000
    with pytest.raises(ImportValidationError, match="sınır"):
        import_orders(
            user=owner,
            store_pk=store.pk,
            upload=csv_upload(
                [
                    row(
                        siparis_no="too-big",
                        adet="2147483647",
                        birim_fiyat_kdv_dahil="9999999999.99",
                    ),
                ]
            ),
        )
    assert not OrderLine.objects.filter(order_number="too-big").exists()


def test_multiline_order_reprices_after_new_line(finance):
    owner, _, store, _ = finance
    import_orders(
        user=owner,
        store_pk=store.pk,
        upload=csv_upload([row(satir_no="2", adet="1", birim_fiyat_kdv_dahil="600")]),
    )
    assert (
        sum(FinancialLine.objects.filter(line__store=store).values_list("shipping", flat=True))
        == 8000
    )
    assert (
        sum(FinancialLine.objects.filter(line__store=store).values_list("service", flat=True))
        == 1000
    )


def test_guardrail_rejects_invented_signed_or_locale_numbers():
    assert guardrail("Kâr 1.234,56 ₺", ["1.234,56"])
    assert not guardrail("Kâr -1.234,56 ₺", ["1.234,56"])
    assert not guardrail("Kâr 999,00 ₺", ["1.234,56"])


def test_assistant_uses_owner_tools_and_isolated_sql(client, finance):
    owner, _, store, foreign = finance
    result = ask(user=owner, store_pk=store.pk, question="2026 Eylül net kârım ne?")
    assert result["tool"]["amounts"]["profit"] == 6000
    assert "60,00 ₺" in result["answer"]
    with pytest.raises(Http404):
        ask(user=owner, store_pk=foreign.pk, question="özet")
    client.force_login(owner)
    response = client.post(
        reverse("assistant:chat", args=[store.pk]), {"question": "Stopaj kârımı nasıl etkiler?"}
    )
    assert "Kâr gideri değildir" in response.content.decode()
    assert tl(123456) == "1.234,56 ₺"
    assert tl(-123456) == "-1.234,56 ₺"
