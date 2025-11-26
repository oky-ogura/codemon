from django.db import migrations


def add_avatar_if_missing(apps, schema_editor):
    """avatarカラムが存在しない場合のみ追加"""
    table = "account"
    conn = schema_editor.connection
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(%s)" % table)
    cols = [row[1] for row in cursor.fetchall()]
    if "avatar" not in cols:
        cursor.execute('ALTER TABLE account ADD COLUMN "avatar" varchar(255) NULL;')


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0006_account_avatar"),
    ]

    operations = [
        migrations.RunPython(add_avatar_if_missing, reverse_code=migrations.RunPython.noop),
    ]
