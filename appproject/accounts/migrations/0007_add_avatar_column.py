from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0006_account_avatar"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE account
            ADD COLUMN IF NOT EXISTS avatar VARCHAR(255);
            """,
            reverse_sql="""
            ALTER TABLE account
            DROP COLUMN IF EXISTS avatar;
            """,
        ),
    ]
