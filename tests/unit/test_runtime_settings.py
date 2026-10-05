import os
import runpy
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from django.core.exceptions import ImproperlyConfigured

from tests.unit.test_production_settings import VALID_TEST_KEY

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[2]


def test_dotenv_controls_assistant_backend(tmp_path):
    shutil.copytree(ROOT / "config", tmp_path / "config")
    (tmp_path / ".env").write_text("KARKONTROL_ASSISTANT_BACKEND=local\n", encoding="utf-8")
    environment = os.environ.copy()
    environment.pop("KARKONTROL_ASSISTANT_BACKEND", None)
    environment["PYTHONPATH"] = str(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from config.settings.local import ASSISTANT_BACKEND; print(ASSISTANT_BACKEND)",
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "local"


@pytest.mark.parametrize("entrypoint", ["wsgi", "asgi"])
def test_server_entrypoints_default_to_production(monkeypatch, entrypoint):
    monkeypatch.delenv("DJANGO_SETTINGS_MODULE", raising=False)
    monkeypatch.setattr(f"django.core.{entrypoint}.get_{entrypoint}_application", lambda: None)
    runpy.run_path(str(ROOT / "config" / f"{entrypoint}.py"))
    assert os.environ["DJANGO_SETTINGS_MODULE"] == "config.settings.production"


def test_production_reads_trusted_proxy_and_csrf_origins(monkeypatch):
    monkeypatch.setenv("DJANGO_SECRET_KEY", VALID_TEST_KEY)
    monkeypatch.setenv("DJANGO_ALLOWED_HOSTS", "demo.example.test")
    monkeypatch.setenv("DJANGO_SECURE_PROXY_SSL_HEADER", "HTTP_X_FORWARDED_PROTO,https")
    monkeypatch.setenv(
        "DJANGO_CSRF_TRUSTED_ORIGINS", "https://demo.example.test, https://api.example.test"
    )
    settings = runpy.run_module("config.settings.production")
    assert settings["SECURE_PROXY_SSL_HEADER"] == ("HTTP_X_FORWARDED_PROTO", "https")
    assert settings["CSRF_TRUSTED_ORIGINS"] == [
        "https://demo.example.test",
        "https://api.example.test",
    ]


@pytest.mark.parametrize(
    "proxy", ["HTTP_X_FORWARDED_PROTO", "X_FORWARDED_PROTO,https", "HTTP_X_FORWARDED_PROTO,"]
)
def test_production_rejects_malformed_proxy_setting(monkeypatch, proxy):
    monkeypatch.setenv("DJANGO_SECRET_KEY", VALID_TEST_KEY)
    monkeypatch.setenv("DJANGO_ALLOWED_HOSTS", "demo.example.test")
    monkeypatch.setenv("DJANGO_SECURE_PROXY_SSL_HEADER", proxy)
    with pytest.raises(ImproperlyConfigured, match="DJANGO_SECURE_PROXY_SSL_HEADER"):
        runpy.run_module("config.settings.production")


@pytest.mark.parametrize(
    "origin", ["demo.example.test", "http://demo.example.test", "https://demo.example.test/path"]
)
def test_production_rejects_invalid_csrf_origins(monkeypatch, origin):
    monkeypatch.setenv("DJANGO_SECRET_KEY", VALID_TEST_KEY)
    monkeypatch.setenv("DJANGO_ALLOWED_HOSTS", "demo.example.test")
    monkeypatch.setenv("DJANGO_CSRF_TRUSTED_ORIGINS", origin)
    with pytest.raises(ImproperlyConfigured, match="DJANGO_CSRF_TRUSTED_ORIGINS"):
        runpy.run_module("config.settings.production")
