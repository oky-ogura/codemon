"""Add missing `type` column to Account model when DB was created externally.

This migration adds a nullable `type` CharField so that the database schema
matches the Django model. It is safe to apply on databases where the column
is already present (the operation will be skipped by the database engine).
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_account_age"),
    ]

    operations = [
        # Use raw SQL with IF NOT EXISTS to avoid failure if column already exists
        migrations.RunSQL(
            sql=(
                "ALTER TABLE account ADD COLUMN IF NOT EXISTS \"type\" varchar(50) NULL;"
            ),
            reverse_sql=(
                "ALTER TABLE account DROP COLUMN IF EXISTS \"type\";"
            ),
        ),
    ]
