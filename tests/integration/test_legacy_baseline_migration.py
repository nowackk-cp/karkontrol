import importlib
from decimal import Decimal
from types import SimpleNamespace

import pytest
from django.db import connection, models

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_migration_repairs_previously_applied_not_null_without_changing_source_data():
    class BaselineProbe(models.Model):
        import_batch = models.IntegerField(null=True)
        imported_returned_quantity = models.PositiveIntegerField(null=True, default=None)
        returned_quantity = models.PositiveIntegerField()
        quantity = models.PositiveIntegerField()
        unit_price_gross = models.DecimalField(max_digits=12, decimal_places=2)

        class Meta:
            app_label = "orders"
            db_table = "orders_legacy_baseline_probe"
            managed = False

    migration = importlib.import_module(
        "apps.orders.migrations.0005_legacy_unknown_return_baseline"
    )
    field = BaselineProbe._meta.get_field("imported_returned_quantity")
    field.null = False
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(BaselineProbe)
    field.null = True
    try:
        legacy = BaselineProbe.objects.create(
            import_batch=None,
            imported_returned_quantity=1,
            returned_quantity=1,
            quantity=2,
            unit_price_gross=Decimal("149.99"),
        )
        current = BaselineProbe.objects.create(
            import_batch=42,
            imported_returned_quantity=1,
            returned_quantity=2,
            quantity=2,
            unit_price_gross=Decimal("600.00"),
        )
        baseline = list(
            BaselineProbe.objects.order_by("pk").values(
                "id", "import_batch", "returned_quantity", "quantity", "unit_price_gross"
            )
        )
        fake_apps = SimpleNamespace(get_model=lambda *args: BaselineProbe)
        for _ in range(2):
            with connection.schema_editor() as schema_editor:
                migration.preserve_unknown_legacy_baseline(fake_apps, schema_editor)
        legacy.refresh_from_db()
        current.refresh_from_db()
        assert legacy.imported_returned_quantity is None
        assert current.imported_returned_quantity == 1
        assert (
            list(
                BaselineProbe.objects.order_by("pk").values(
                    "id", "import_batch", "returned_quantity", "quantity", "unit_price_gross"
                )
            )
            == baseline
        )
        with connection.cursor() as cursor:
            columns = connection.introspection.get_table_description(
                cursor, BaselineProbe._meta.db_table
            )
        assert next(column for column in columns if column.name == field.column).null_ok
    finally:
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(BaselineProbe)
