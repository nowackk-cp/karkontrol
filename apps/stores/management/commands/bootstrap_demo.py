from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Initialize local demo database and reports."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Demo kurulumu yalnız DEBUG açıkken kullanılabilir.")
        call_command("migrate", interactive=False)
        call_command("seed_demo")
        call_command("rebuild_reports")
