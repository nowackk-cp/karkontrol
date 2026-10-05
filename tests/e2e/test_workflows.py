from decimal import Decimal

import pytest
from playwright.sync_api import expect

from apps.orders.models import FinancialLine, ImportBatch, OrderLine
from tests.integration.test_stores_orders import csv_upload, row

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


def money_text(cents):
    # Locale contract only; no profit calculation or golden expectation generation.
    value = Decimal(cents) / Decimal("100")
    return f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".") + " ₺"


def snapshot():
    return {
        model.__name__: list(model.objects.order_by("pk").values())
        for model in [OrderLine, ImportBatch, FinancialLine]
    }


def test_login_logout(workspace):
    ui = workspace["ui"]
    ui.login()
    ui.login_screen.logout()


def test_store_setup(workspace):
    ui = workspace["ui"]
    ui.login()
    ui.store_form.create("Yeni Amazon", marketplace="amazon_demo", commission="15")


def test_bad_commission(workspace):
    ui = workspace["ui"]
    ui.login()
    ui.store_form.create("Geçersiz", commission="150", error="100")


def test_excel_import_30(workspace):
    ui = workspace["ui"]
    ui.login()
    ui.upload_screen.submit(workspace["xlsx"], message="30 sipariş satırı aktarıldı")
    assert OrderLine.objects.filter(store=workspace["store"]).count() == 30


def test_missing_columns_atomic(workspace):
    ui = workspace["ui"]
    ui.login()
    ui.upload_screen.submit(workspace["invalid"], error="Eksik sütunlar")
    assert not OrderLine.objects.filter(store=workspace["store"]).exists()


def test_duplicate_import(workspace):
    ui = workspace["ui"]
    ui.login()
    ui.upload_screen.submit(workspace["xlsx"], message="30 sipariş satırı aktarıldı")
    ui.upload_screen.submit(workspace["xlsx"], message="0 sipariş satırı aktarıldı; 30 mevcut")
    assert OrderLine.objects.filter(store=workspace["store"]).count() == 30


def test_user_example_cards_and_turkish_format(imported):
    report = imported["ui"].report_screen
    report.show()
    # Existing 600 TL example published in KURALLAR_v1; multiplication by 30
    # checks browser presentation of that example, not a new human golden set.
    expect(report.card("profit")).to_have_text("1.800,00 ₺")
    expect(report.card("payout")).to_have_text("11.010,00 ₺")
    expect(report.card("sales")).to_have_text("15.000,00 ₺")


def test_five_distinct_policy_rows_show_every_column(varied_imported):
    ui = varied_imported["ui"]
    ui.report_screen.show()
    lines = list(
        OrderLine.objects.filter(store=varied_imported["store"]).select_related("financial")
    )
    expect(ui.report_screen.rows()).to_have_count(5)
    fields = {
        "sales": "net_sales",
        "commission": "commission",
        "shipping": "shipping",
        "service": "service",
        "cost": "cost",
        "withholding": "withholding",
        "profit": "profit",
        "payout": "payout",
    }
    for index, line in enumerate(lines):
        displayed = ui.report_screen.rows().nth(index)
        expect(displayed.get_by_test_id("line-order")).to_contain_text(
            f"{line.order_number} / {line.line_number}"
        )
        expect(displayed.get_by_test_id("line-order")).to_contain_text(
            line.order_date.strftime("%d.%m.%Y")
        )
        expect(displayed.get_by_test_id("line-order")).to_contain_text(
            f"{line.quantity} adet / {line.returned_quantity} iade"
        )
        expect(displayed.get_by_test_id("line-product")).to_contain_text(line.product_name)
        expect(displayed.get_by_test_id("line-product")).to_contain_text(line.sku)
        expect(displayed.get_by_test_id("line-product")).to_contain_text(line.currency)
        for selector, attribute in fields.items():
            cents = getattr(line.financial, attribute)
            expect(displayed.get_by_test_id(f"line-{selector}")).to_have_text(money_text(cents))
            expect(displayed.get_by_test_id(f"line-{selector}")).to_have_attribute(
                "data-cents", str(cents)
            )


def test_row_sum_equals_all_cards(imported):
    ui = imported["ui"]
    ui.report_screen.show()
    for column, card in [("profit", "profit"), ("payout", "payout"), ("sales", "sales")]:
        values = ui.page.get_by_test_id(f"line-{column}").evaluate_all(
            "elements => elements.map(e => e.dataset.cents)"
        )
        total = ui.report_screen.card(card).get_attribute("data-cents")
        assert sum(map(int, values)) == int(total)


def test_date_and_product_filters_exclude_real_rows(varied_imported):
    ui = varied_imported["ui"]
    report = ui.report_screen
    report.show()
    expect(report.rows()).to_have_count(5)
    report.filter(start="2026-09-01", end="2026-09-02", count=3)
    expect(report.rows()).to_have_count(3)
    assert report.rows().evaluate_all("rows => rows.map(row => row.dataset.orderNumber)") == [
        "POLICY-COUPON",
        "POLICY-DISCOUNT",
        "POLICY-BASE",
    ]
    report.filter(start="2026-09-01", end="2026-09-02", product="SALE", count=1)
    expect(report.rows()).to_have_count(1)
    expect(report.rows().get_by_test_id("line-order")).to_contain_text("POLICY-DISCOUNT")
    selected = OrderLine.objects.get(store=varied_imported["store"], sku="SALE").financial
    for column, field in [("profit", "profit"), ("payout", "payout"), ("sales", "net_sales")]:
        expect(report.card(column)).to_have_attribute("data-cents", str(getattr(selected, field)))
    report.filter(start="2026-10-01", end="2026-10-02", product="SALE", count=0)
    expect(report.rows()).to_have_count(0)
    for column in ["profit", "payout", "sales"]:
        expect(report.card(column)).to_have_text("0,00 ₺")


def test_return_updates_profit(imported):
    ui = imported["ui"]
    line = OrderLine.objects.filter(store=imported["store"]).first()
    ui.return_form.submit(line.pk, 1)
    ui.report_screen.show()
    expect(ui.report_screen.card("profit")).to_have_text("1.620,00 ₺")


def test_limit_and_payment_outcomes(workspace, tmp_path):
    from apps.orders.importing import import_orders

    ui = workspace["ui"]
    import_orders(
        user=workspace["owner"],
        store_pk=workspace["store"].pk,
        upload=csv_upload([row(siparis_no=f"L{i}") for i in range(100)]),
    )
    excess = tmp_path / "extra.csv"
    excess.write_bytes(csv_upload([row(siparis_no="EXCESS")]).read())
    ui.login()
    ui.upload_screen.submit(excess, error="100 satır")
    for outcome, plan, message in [
        ("failed", "Ücretsiz", "Sahte ödeme reddedildi"),
        ("timeout", "Ücretsiz", "Sahte ödeme zaman aşımına uğradı"),
        ("success", "Demo Pro", "Demo Pro etkinleştirildi"),
    ]:
        ui.subscription.pay(outcome, plan=plan, message=message)
    ui.upload_screen.submit(excess, message="1 sipariş satırı aktarıldı")


def test_other_tenant_get_and_post_leave_database_unchanged(workspace):
    from apps.orders.importing import import_orders

    ui = workspace["ui"]
    foreign = workspace["foreign"]
    import_orders(user=foreign.owner, store_pk=foreign.pk, upload=csv_upload([row()]))
    line = OrderLine.objects.get(store=foreign)
    ui.login()
    before = snapshot()
    response = ui.open(f"/stores/{foreign.pk}/reports/")
    assert response.status == 404
    # Fetch our own CSRF cookie first, so POST 404 exercises ownership rather
    # than being rejected earlier by CSRF middleware.
    ui.open(f"/stores/{ui.store_pk}/orders/upload/")
    csrf = next(
        cookie["value"] for cookie in ui.page.context.cookies() if cookie["name"] == "csrftoken"
    )
    response = ui.page.request.post(
        ui.base_url + f"/stores/{foreign.pk}/orders/upload/",
        headers={"X-CSRFToken": csrf, "Referer": ui.base_url},
        multipart={
            "file": {
                "name": "foreign.csv",
                "mimeType": "text/csv",
                "buffer": csv_upload([row(siparis_no="FORGED")]).read(),
            }
        },
    )
    assert response.status == 404
    response = ui.page.request.post(
        ui.base_url + f"/stores/{foreign.pk}/orders/{line.pk}/return/",
        headers={"X-CSRFToken": csrf, "Referer": ui.base_url},
        form={"returned_quantity": "1"},
    )
    assert response.status == 404
    assert snapshot() == before
