"""Yalnızca yerel geliştirme. .env bu modülde yüklenir."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)

from .base import *  # noqa: E402, F403

DEBUG = True
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY") or "django-insecure-karkontrol-local-development-only"
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]").split(",")
    if host.strip()
]
