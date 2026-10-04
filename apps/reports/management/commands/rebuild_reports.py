from django.core.management.base import BaseCommand
from django.db import transaction

from apps.orders.models import OrderLine
from apps.reports.services import check_report_bounds, recalculate_order
from apps.stores.models import Store


class Command(BaseCommand):
    help = "Mevcut siparişlerin demo-v1 hesap kayıtlarını atomik olarak yeniden oluşturur."

    @transaction.atomic
    def handle(self, *args, **options):
        count = 0
        for store in Store.objects.all():
            for number in (
                OrderLine.objects.filter(store=store)
                .order_by("order_number")
                .values_list("order_number", flat=True)
                .distinct()
            ):
                recalculate_order(store, number, enforce_totals=False)
                count += 1
            check_report_bounds(store)
        self.stdout.write(self.style.SUCCESS(f"{count} sipariş hesaplandı."))
