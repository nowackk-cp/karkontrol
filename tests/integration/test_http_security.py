from types import SimpleNamespace

import pytest
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadhandler import StopUpload
from django.http import HttpRequest
from django.test import Client, override_settings
from django.urls import URLPattern, URLResolver, get_resolver, reverse

from apps.orders.importing import import_orders
from apps.orders.models import FinancialLine, ImportBatch, OrderLine
from apps.stores.models import Store
from config.security import LimitedUploadHandler
from tests.integration.test_stores_orders import csv_upload, row

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture(autouse=True)
def isolated_login_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def security_store(django_user_model):
    owner = django_user_model.objects.create_user(
        "security-owner", password="synthetic-security-pass"
    )
    other = django_user_model.objects.create_user(
        "security-other", password="synthetic-security-pass"
    )
    store = Store.objects.create(owner=owner, name="Security store")
    import_orders(user=owner, store_pk=store.pk, upload=csv_upload([row()]))
    return owner, other, store


def database_snapshot():
    return {
        model.__name__: list(model.objects.order_by("pk").values())
        for model in [Store, OrderLine, ImportBatch, FinancialLine]
    }


def store_routes(patterns=None, namespace="", converters=None):
    """Discover new store endpoints automatically, including included URL modules."""
    converters = converters or {}
    for pattern in patterns or get_resolver().url_patterns:
        inherited = converters | pattern.pattern.converters
        if isinstance(pattern, URLResolver):
            nested = namespace + (pattern.namespace + ":" if pattern.namespace else "")
            yield from store_routes(pattern.url_patterns, nested, inherited)
        elif isinstance(pattern, URLPattern) and "store_pk" in inherited:
            assert pattern.name, "Store routes must have names for ownership coverage"
            yield namespace + pattern.name, inherited


@pytest.mark.parametrize("method", ["get", "post"])
def test_every_store_route_requires_login_and_ownership(client, security_store, method):
    owner, other, store = security_store
    line = OrderLine.objects.get(store=store)
    batch = ImportBatch.objects.get(store=store)
    identifiers = {"store_pk": store.pk, "pk": line.pk, "batch_pk": batch.pk}
    before = database_snapshot()
    routes = list(store_routes())
    assert len(routes) >= 7
    for name, converters in routes:
        assert set(converters) <= identifiers.keys(), f"Add identifiers for {name}"
        url = reverse(name, kwargs={key: identifiers[key] for key in converters})
        client.logout()
        assert getattr(client, method)(url).status_code == 302, name
        client.force_login(other)
        assert getattr(client, method)(url).status_code == 404, name
    assert database_snapshot() == before


def test_state_changing_views_require_csrf(security_store):
    owner, _, store = security_store
    line = OrderLine.objects.get(store=store)
    batch = ImportBatch.objects.get(store=store)
    identifiers = {"store_pk": store.pk, "pk": line.pk, "batch_pk": batch.pk}
    urls = [
        reverse(name, kwargs={key: identifiers[key] for key in fields})
        for name, fields in store_routes()
    ]
    urls += [
        reverse(name)
        for name in ["stores:create", "billing:subscription", "logout", "signup", "login"]
    ]
    csrf_client = Client(enforce_csrf_checks=True)
    csrf_client.force_login(owner)
    before = database_snapshot()
    for url in urls:
        assert csrf_client.post(url, {}).status_code == 403, url
    assert database_snapshot() == before


@pytest.mark.parametrize("password", ["123", "1234567890", "password"])
def test_signup_rejects_weak_passwords(client, django_user_model, password):
    response = client.post(
        reverse("signup"),
        {"username": "weak-new-account", "password1": password, "password2": password},
    )
    assert response.status_code == 200
    assert response.context["form"].errors["password2"]
    assert not django_user_model.objects.filter(username="weak-new-account").exists()


def test_oversized_http_upload_stops_before_import(client, security_store, monkeypatch):
    owner, _, store = security_store
    client.force_login(owner)
    called = []

    def import_spy(**kwargs):
        called.append(kwargs)
        return SimpleNamespace(created=0, skipped=0)

    monkeypatch.setattr("apps.orders.views.import_orders", import_spy)
    before = database_snapshot()
    response = client.post(
        reverse("orders:upload", args=[store.pk]),
        {"file": SimpleUploadedFile("large.csv", b"x" * (5 * 1024 * 1024 + 1))},
    )
    assert response.status_code == 413
    assert not called
    assert database_snapshot() == before


def test_login_attempts_are_limited_and_window_expires(client, security_store):
    owner, _, _ = security_store
    cache.clear()
    with override_settings(LOGIN_RATE_LIMIT_ATTEMPTS=2, LOGIN_RATE_LIMIT_WINDOW=60):
        for _ in range(2):
            assert (
                client.post(
                    reverse("login"), {"username": owner.username, "password": "wrong"}
                ).status_code
                == 200
            )
        blocked = client.post(
            reverse("login"), {"username": owner.username, "password": "synthetic-security-pass"}
        )
        assert blocked.status_code == 429
        assert int(blocked["Retry-After"]) > 0
        assert "_auth_user_id" not in client.session
        # Expire the configured in-memory cache deadlines without sleeping.
        for key in cache._expire_info:
            cache._expire_info[key] = 0
        assert (
            client.post(
                reverse("login"),
                {"username": owner.username, "password": "synthetic-security-pass"},
            ).status_code
            == 302
        )


def test_total_upload_limit_blocks_completed_first_file_before_import(
    client, security_store, monkeypatch
):
    owner, _, store = security_store
    client.force_login(owner)
    called = []

    def import_spy(**kwargs):
        called.append(kwargs)
        return SimpleNamespace(created=0, skipped=0)

    monkeypatch.setattr("apps.orders.views.import_orders", import_spy)
    before = database_snapshot()
    response = client.post(
        reverse("orders:upload", args=[store.pk]),
        {
            "file": [
                csv_upload([row(siparis_no="FIRST-VALID")]),
                SimpleUploadedFile("oversize.csv", b"x" * (5 * 1024 * 1024)),
            ]
        },
    )
    assert response.status_code == 413
    assert not called
    assert database_snapshot() == before


def test_upload_handler_hard_boundary_and_aggregates_multiple_files():
    request = HttpRequest()
    handler = LimitedUploadHandler(request)
    chunk = b"x" * (5 * 1024 * 1024)
    assert handler.receive_data_chunk(chunk, 0) is chunk
    assert not hasattr(request, "karkontrol_upload_too_large")
    handler.new_file("file", "second.csv", "text/csv", 1)
    with pytest.raises(StopUpload):
        handler.receive_data_chunk(b"x", 0)
    assert request.karkontrol_upload_too_large


def test_ip_limit_cannot_be_bypassed_by_usernames_or_forwarded_header(client):
    with override_settings(LOGIN_RATE_LIMIT_IP_ATTEMPTS=2):
        for index in range(2):
            response = client.post(
                reverse("login"),
                {"username": f"unknown-{index}", "password": "wrong"},
                HTTP_X_FORWARDED_FOR=f"10.0.0.{index}",
            )
            assert response.status_code == 200
        assert (
            client.post(
                reverse("login"),
                {"username": "new-name", "password": "wrong"},
                HTTP_X_FORWARDED_FOR="10.0.0.99",
            ).status_code
            == 429
        )


def test_rate_limit_does_not_lock_another_ip(client, security_store):
    owner, _, _ = security_store
    with override_settings(LOGIN_RATE_LIMIT_ATTEMPTS=1):
        client.post(
            reverse("login"),
            {"username": owner.username, "password": "wrong"},
            REMOTE_ADDR="192.0.2.1",
        )
        response = client.post(
            reverse("login"),
            {"username": owner.username, "password": "synthetic-security-pass"},
            REMOTE_ADDR="192.0.2.2",
        )
        assert response.status_code == 302
