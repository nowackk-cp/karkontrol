"""Sadece yerel DEBUG ortamında sentetik bir demo hesap kurar."""

import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.orders.importing import REQUIRED_COLUMNS, import_orders
from apps.stores.models import Store


class Command(BaseCommand):
    help = "Yerel demo verisi kurar. Kullanıcı: demo-satici; varsayılan parola: demo-only-pass-2026"

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Demo kurulumu yalnızca DEBUG açık yerel geliştirmede çalışır.")
        password = os.environ.get("KARKONTROL_DEMO_PASSWORD", "demo-only-pass-2026")
        with transaction.atomic():
            user, created = get_user_model().objects.get_or_create(username="demo-satici")
            if created:
                user.set_password(password)
                user.save(update_fields=["password"])
            elif not user.check_password(password) or user.is_staff or user.is_superuser:
                raise CommandError(
                    "Mevcut demo-satici hesabı değiştirilmedi; farklı hesap kullanıyor."
                )
            store, _ = Store.objects.get_or_create(owner=user, name="Sentetik Demo Mağazası")
            content = (
                ";".join(REQUIRED_COLUMNS) + "\n"
                "DEMO-001;1;2026-09-01;Sentetik fincan;DEMO-A;2;149,99;20;50,00\n"
                "DEMO-002;1;2026-09-15;Sentetik çanta;DEMO-B;1;1234,56;10;400,00\n"
            )
            import_orders(
                user=user,
                store_pk=store.pk,
                upload=SimpleUploadedFile("demo.csv", content.encode("utf-8")),
            )
        self.stdout.write(self.style.SUCCESS("Sentetik demo hazır. Kullanıcı: demo-satici"))
