"""Üretim için zorunlu ortam değişkenleri ve güvenli varsayılanlar."""

import os
from urllib.parse import urlsplit

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403

DEBUG = False
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
if len(SECRET_KEY) < 50 or len(set(SECRET_KEY)) < 5 or SECRET_KEY.startswith("django-insecure-"):
    raise ImproperlyConfigured("DJANGO_SECRET_KEY en az 50 karakterlik güçlü bir anahtar olmalı.")
ALLOWED_HOSTS = [
    host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if host.strip()
]
if not ALLOWED_HOSTS or "*" in ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "DJANGO_ALLOWED_HOSTS açıkça tanımlanmalı; joker alan adı kullanılamaz."
    )

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

proxy = os.getenv("DJANGO_SECURE_PROXY_SSL_HEADER", "").strip()
SECURE_PROXY_SSL_HEADER = None
if proxy:
    parts = tuple(part.strip() for part in proxy.split(","))
    if len(parts) != 2 or not parts[0].startswith("HTTP_") or not parts[1]:
        raise ImproperlyConfigured(
            "DJANGO_SECURE_PROXY_SSL_HEADER HTTP_X_FORWARDED_PROTO,https biçiminde olmalı."
        )
    SECURE_PROXY_SSL_HEADER = parts

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]
for origin in CSRF_TRUSTED_ORIGINS:
    parsed = urlsplit(origin)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.path
        or parsed.query
        or parsed.fragment
    ):
        raise ImproperlyConfigured("DJANGO_CSRF_TRUSTED_ORIGINS HTTPS origin adresleri içermeli.")
