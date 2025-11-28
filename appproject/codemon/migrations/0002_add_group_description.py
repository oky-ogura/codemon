from django.db import migrations, models


def add_description_if_missing(apps, schema_editor):
    table = "group"
    conn = schema_editor.connection
    cursor = conn.cursor()
    # quote table name to avoid issues with reserved words
    cursor.execute("PRAGMA table_info('group')")
    cols = [row[1] for row in cursor.fetchall()]
    if "description" not in cols:
        cursor.execute(
            'ALTER TABLE "group" ADD COLUMN "description" TEXT NULL;'
        )


class Migration(migrations.Migration):

    dependencies = [
        ("codemon", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_description_if_missing, reverse_code=migrations.RunPython.noop),
    ]