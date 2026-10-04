import pytest

from apps.orders.importing import import_orders
from apps.stores.models import Store
from tests.integration.test_stores_orders import csv_upload, row, xlsx_upload

from .pages.workspace import Workspace


@pytest.fixture(scope="session", autouse=True)
def synchronous_browser_test_only():
    # Playwright's sync adapter owns an event loop; only these isolated test fixtures
    # use the ORM in that thread. Never set this flag in application settings.
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("DJANGO_ALLOW_ASYNC_UNSAFE", "true")
        yield


@pytest.fixture
def workspace(page, live_server, django_user_model, tmp_path):
    owner = django_user_model.objects.create_user("e2e-owner", password="synthetic-browser-pass")
    other = django_user_model.objects.create_user("e2e-other", password="synthetic-browser-pass")
    store = Store.objects.create(owner=owner, name="Tarayıcı mağazası")
    foreign = Store.objects.create(owner=other, name="Yabancı mağaza")
    records = [
        row(
            siparis_no=f"E2E-{i:02d}",
            adet="1",
            birim_fiyat_kdv_dahil="600",
            birim_maliyet_kdv_haric="250",
            urun_kodu="SKU-600",
        )
        for i in range(30)
    ]
    xlsx = tmp_path / "thirty.xlsx"
    xlsx.write_bytes(xlsx_upload(records).read())
    invalid = tmp_path / "missing.csv"
    invalid.write_text("siparis_no;adet\nBAD;1\n", encoding="utf-8")
    ui = Workspace(page, live_server.url, store.pk)
    return {
        "ui": ui,
        "owner": owner,
        "store": store,
        "foreign": foreign,
        "xlsx": xlsx,
        "invalid": invalid,
        "records": records,
    }


@pytest.fixture
def imported(workspace):
    import_orders(
        user=workspace["owner"],
        store_pk=workspace["store"].pk,
        upload=csv_upload(workspace["records"]),
    )
    workspace["ui"].login()
    return workspace
