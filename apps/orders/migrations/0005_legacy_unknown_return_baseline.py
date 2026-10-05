from django.db import migrations, models


def preserve_unknown_legacy_baseline(apps, schema_editor):
    lines = apps.get_model("orders", "OrderLine")
    connection = schema_editor.connection
    field = lines._meta.get_field("imported_returned_quantity")
    with connection.cursor() as cursor:
        description = connection.introspection.get_table_description(cursor, lines._meta.db_table)
    stored_field = next(item for item in description if item.name == field.column)
    if not stored_field.null_ok:
        # An earlier local 0004 was applied with NOT NULL before its final source
        # became nullable. Migration state alone cannot detect that physical schema.
        old_field = field.clone()
        old_field.set_attributes_from_name(field.name)
        old_field.model = lines
        old_field.null = False
        old_field.blank = False
        old_field.default = 0
        schema_editor.alter_field(lines, old_field, field, strict=True)
    lines.objects.using(connection.alias).filter(import_batch__isnull=True).update(
        imported_returned_quantity=None
    )


class Migration(migrations.Migration):
    dependencies = [("orders", "0004_import_sources_turkish_search")]

    operations = [
        migrations.RunPython(preserve_unknown_legacy_baseline, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="orderline",
            name="imported_returned_quantity",
            field=models.PositiveIntegerField(blank=True, default=None, editable=False, null=True),
        ),
    ]
