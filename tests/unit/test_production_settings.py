import runpy

import pytest
from django.core.exceptions import ImproperlyConfigured

pytestmark = pytest.mark.unit

VALID_TEST_KEY = "test-only-" + "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


@pytest.mark.parametrize("key", ["", "short", "a" * 60, "django-insecure-" + "x" * 60])
def test_production_refuses_unsafe_secret(monkeypatch, key):
    monkeypatch.setenv("DJANGO_SECRET_KEY", key)
    monkeypatch.setenv("DJANGO_ALLOWED_HOSTS", "demo.example.test")
    with pytest.raises(ImproperlyConfigured, match="DJANGO_SECRET_KEY"):
        runpy.run_module("config.settings.production")


@pytest.mark.parametrize("hosts", ["", "   ", "*", "demo.example.test,*"])
def test_production_requires_explicit_hosts(monkeypatch, hosts):
    monkeypatch.setenv("DJANGO_SECRET_KEY", VALID_TEST_KEY)
    monkeypatch.setenv("DJANGO_ALLOWED_HOSTS", hosts)
    with pytest.raises(ImproperlyConfigured, match="DJANGO_ALLOWED_HOSTS"):
        runpy.run_module("config.settings.production")


def test_production_enforces_https_and_secure_cookies(monkeypatch):
    monkeypatch.setenv("DJANGO_SECRET_KEY", VALID_TEST_KEY)
    monkeypatch.setenv("DJANGO_ALLOWED_HOSTS", " demo.example.test, api.example.test ")
    settings = runpy.run_module("config.settings.production")
    assert settings["DEBUG"] is False
    assert settings["ALLOWED_HOSTS"] == ["demo.example.test", "api.example.test"]
    assert settings["SECURE_SSL_REDIRECT"] is True
    assert settings["SESSION_COOKIE_SECURE"] is True
    assert settings["CSRF_COOKIE_SECURE"] is True
    assert settings["SECURE_HSTS_SECONDS"] == 31536000
