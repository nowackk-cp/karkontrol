from unittest.mock import patch

import pytest
from django.db import OperationalError
from django.test import Client
from django.urls import reverse

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def account(django_user_model):
    return django_user_model.objects.create_user("sentetik-satici", password="test-only-password")


def test_health_checks_database(client):
    response = client.get(reverse("health"))
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_returns_503_without_exposing_database_details(client):
    with patch("config.views.connection.cursor", side_effect=OperationalError("private-db-path")):
        response = client.get(reverse("health"))
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}
    assert b"private-db-path" not in response.content


@pytest.mark.parametrize("url", ["home", "health"])
def test_read_only_endpoints_reject_post(client, url):
    assert client.post(reverse(url)).status_code == 405


def test_login_creates_session_and_logout_invalidates_it(client, account):
    response = client.post(
        reverse("login"), {"username": account.username, "password": "test-only-password"}
    )
    assert response.status_code == 302
    assert response.url == reverse("home")
    assert client.session["_auth_user_id"] == str(account.pk)
    assert account.username.encode() in client.get(reverse("home")).content
    assert client.post(reverse("logout")).status_code == 302
    assert "_auth_user_id" not in client.session


def test_invalid_credentials_do_not_create_session(client, account):
    response = client.post(reverse("login"), {"username": account.username, "password": "wrong"})
    assert response.status_code == 200
    assert response.context["form"].non_field_errors()
    assert "_auth_user_id" not in client.session


def test_login_rejects_external_redirect(client, account):
    response = client.post(
        reverse("login"),
        {
            "username": account.username,
            "password": "test-only-password",
            "next": "https://evil.test",
        },
    )
    assert response.status_code == 302
    assert response.url == reverse("home")


def test_logout_requires_post(client, account):
    client.force_login(account)
    assert client.get(reverse("logout")).status_code == 405
    assert client.session["_auth_user_id"] == str(account.pk)


def test_login_requires_csrf_token(account):
    client = Client(enforce_csrf_checks=True)
    response = client.post(
        reverse("login"), {"username": account.username, "password": "test-only-password"}
    )
    assert response.status_code == 403
    assert "_auth_user_id" not in client.session


def test_logout_requires_csrf_token(account):
    client = Client(enforce_csrf_checks=True)
    client.force_login(account)
    assert client.post(reverse("logout")).status_code == 403
    assert client.session["_auth_user_id"] == str(account.pk)


def test_anonymous_user_cannot_access_admin(client):
    response = client.get(reverse("admin:index"))
    assert response.status_code == 302
    assert response.url.startswith(reverse("admin:login"))


def test_regular_user_cannot_access_admin(client, account):
    client.force_login(account)
    assert client.get(reverse("admin:index")).status_code == 302


def test_username_is_escaped_in_home_page(client, django_user_model):
    account = django_user_model.objects.create_user(username="<script>alert(1)</script>")
    client.force_login(account)
    response = client.get(reverse("home"))
    assert b"<script>alert(1)</script>" not in response.content
    assert b"&lt;script&gt;" in response.content
