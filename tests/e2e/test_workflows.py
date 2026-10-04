import pytest
from playwright.sync_api import expect

from apps.orders.models import OrderLine
from tests.integration.test_stores_orders import csv_upload, row

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


def test_login_logout(workspace):
    ui = workspace["ui"]
    ui.login()
    ui.page.get_by_test_id("logout").click()
    expect(ui.page.get_by_test_id("login-link")).to_be_visible()


def test_store_setup(workspace):
    ui = workspace["ui"]
    ui.login()
    ui.open("/stores/new/")
    ui.page.get_by_test_id("store-name").fill("Yeni Amazon")
    ui.page.get_by_test_id("store-marketplace").select_option("amazon_demo")
    ui.page.get_by_test_id("store-commission_percent").fill("15")
    ui.page.get_by_test_id("store-save").click()
    expect(ui.page.get_by_role("heading", name="Yeni Amazon")).to_be_visible()


def test_bad_commission(workspace):
    ui = workspace["ui"]
    ui.login()
    ui.open("/stores/new/")
    ui.page.get_by_test_id("store-name").fill("Geçersiz")
    ui.page.get_by_test_id("store-commission_percent").fill("150")
    ui.page.get_by_test_id("store-save").click()
    expect(ui.page.locator(".errorlist")).to_contain_text("100")


def test_excel_import_30(workspace):
    ui = workspace["ui"]
    ui.login()
    ui.upload(workspace["xlsx"])
    expect(ui.page.get_by_test_id("messages")).to_contain_text("30 sipariş satırı aktarıldı")
    assert OrderLine.objects.filter(store=workspace["store"]).count() == 30


def test_missing_columns_atomic(workspace):
    ui = workspace["ui"]
    ui.login()
    ui.upload(workspace["invalid"])
    expect(ui.page.locator(".errorlist")).to_contain_text("Eksik sütunlar")
    assert not OrderLine.objects.filter(store=workspace["store"]).exists()


def test_duplicate_import(workspace):
    ui = workspace["ui"]
    ui.login()
    ui.upload(workspace["xlsx"])
    ui.upload(workspace["xlsx"])
    expect(ui.page.get_by_test_id("messages")).to_contain_text(
        "0 sipariş satırı aktarıldı; 30 mevcut"
    )
    assert OrderLine.objects.filter(store=workspace["store"]).count() == 30


def test_five_user_example_rows_and_turkish_format(imported):
    ui = imported["ui"]
    expect(ui.report()).to_have_text("1.800,00 ₺")
    values = ui.page.get_by_test_id("line-profit")
    for index in range(5):
        expect(values.nth(index)).to_have_text("60,00 ₺")


def test_row_sum_equals_card(imported):
    ui = imported["ui"]
    ui.report()
    values = ui.page.get_by_test_id("line-profit").evaluate_all(
        "elements => elements.map(e => e.dataset.cents)"
    )
    card = ui.page.get_by_test_id("total-profit").get_attribute("data-cents")
    assert sum(map(int, values)) == int(card)


def test_filtered_totals(imported):
    ui = imported["ui"]
    ui.report()
    ui.page.locator("#id_start").fill("2026-09-01")
    ui.page.locator("#id_end").fill("2026-09-01")
    ui.page.locator("#id_product").fill("absent")
    ui.page.get_by_test_id("report-filter").click()
    expect(ui.page.get_by_test_id("total-profit")).to_have_text("0,00 ₺")
    ui.page.locator("#id_product").fill("SKU-600")
    ui.page.get_by_test_id("report-filter").click()
    expect(ui.page.get_by_test_id("total-profit")).to_have_text("1.800,00 ₺")


def test_return_updates_profit(imported):
    ui = imported["ui"]
    line = OrderLine.objects.filter(store=imported["store"]).first()
    ui.open(f"/stores/{ui.store_pk}/orders/{line.pk}/return/")
    ui.page.locator("#id_returned_quantity").fill("1")
    ui.page.get_by_test_id("return-save").click()
    expect(ui.report()).to_have_text("1.620,00 ₺")


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
    ui.upload(excess)
    expect(ui.page.locator(".errorlist")).to_contain_text("100 satır")
    for outcome, plan in [("failed", "Ücretsiz"), ("timeout", "Ücretsiz"), ("success", "Demo Pro")]:
        ui.open("/subscription/")
        ui.page.locator("#id_outcome").select_option(outcome)
        ui.page.get_by_test_id("demo-pay").click()
        expect(ui.page.get_by_test_id("active-plan")).to_have_text(plan)
    ui.upload(excess)
    expect(ui.page.get_by_test_id("messages")).to_contain_text("1 sipariş satırı aktarıldı")


def test_other_tenant_url_denied(workspace):
    ui = workspace["ui"]
    ui.login()
    response = ui.open(f"/stores/{workspace['foreign'].pk}/reports/")
    assert response.status == 404
    expect(ui.page.get_by_text("Yabancı mağaza", exact=True)).to_have_count(0)
