"""Testler geliştirme makinesinin .env dosyasına veya verilerine bağımlı değildir."""

from .base import *  # noqa: F403

DEBUG = False
SECRET_KEY = "django-insecure-karkontrol-tests-only"
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-security",
    }
}
