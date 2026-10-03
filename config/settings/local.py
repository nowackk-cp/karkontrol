"""Yalnızca yerel geliştirme. .env bu modülde yüklenir."""

import os

from dotenv import load_dotenv

from .base import *  # noqa: F403
from .base import BASE_DIR

load_dotenv(BASE_DIR / ".env", override=False)
DEBUG = True
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY") or "django-insecure-karkontrol-local-development-only"
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]").split(",")
    if host.strip()
]
