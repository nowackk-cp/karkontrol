import pytest

from apps.orders.importing import import_orders
from apps.stores.models import Store
from tests.integration.test_stores_orders import csv_upload, row


@pytest.fixture
def evaluation(django_user_model):
    owner = django_user_model.objects.create_user("eval-owner")
    other = django_user_model.objects.create_user("eval-other")
    store = Store.objects.create(owner=owner, name="Eval selected")
    foreign = Store.objects.create(owner=other, name="Eval other")
    rows = [
        row(
            siparis_no="EVAL-A",
            adet="1",
            birim_fiyat_kdv_dahil="600",
            birim_maliyet_kdv_haric="250",
            urun_kodu="A",
        ),
        row(
            siparis_no="EVAL-B",
            tarih="2026-09-30",
            adet="1",
            birim_fiyat_kdv_dahil="600",
            birim_maliyet_kdv_haric="250",
            urun_kodu="B",
            iade_adet="1",
        ),
        row(
            siparis_no="EVAL-C",
            tarih="2026-10-01",
            adet="1",
            birim_fiyat_kdv_dahil="600",
            birim_maliyet_kdv_haric="250",
            urun_kodu="C",
        ),
    ]
    import_orders(user=owner, store_pk=store.pk, upload=csv_upload(rows))
    import_orders(
        user=other,
        store_pk=foreign.pk,
        upload=csv_upload([row(siparis_no="SECRET", birim_fiyat_kdv_dahil="9999")]),
    )
    return owner, store
