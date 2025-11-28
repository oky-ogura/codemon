"""Add missing `type` column to Account model when DB was created externally.

This migration adds a nullable `type` CharField so that the database schema
matches the Django model. SQLite does not support `ALTER TABLE ... ADD COLUMN
IF NOT EXISTS`, so use a Python operation that checks existing columns and
adds the column only when missing. The reverse is a no-op for safety.
"""
from django.db import migrations


def add_type_if_missing(apps, schema_editor):
    table = "account"
    conn = schema_editor.connection
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(%s)" % table)
    cols = [row[1] for row in cursor.fetchall()]
    if "type" not in cols:
        cursor.execute('ALTER TABLE account ADD COLUMN "type" varchar(50) NULL;')


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_account_age"),
    ]

    operations = [
        migrations.RunPython(add_type_if_missing, reverse_code=migrations.RunPython.noop),
    ]