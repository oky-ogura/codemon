# Generated migration file for avatar field

from django.db import migrations, models


def add_account_type_if_missing(apps, schema_editor):
    """account_typeカラムが存在しない場合のみ追加"""
    table = "account"
    conn = schema_editor.connection
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(%s)" % table)
    cols = [row[1] for row in cursor.fetchall()]
    if "account_type" not in cols:
        cursor.execute('ALTER TABLE account ADD COLUMN "account_type" varchar(20) NULL;')


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_remove_account_avatar_remove_account_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/', verbose_name='アバター画像'),
        ),
        migrations.RunPython(add_account_type_if_missing, reverse_code=migrations.RunPython.noop),
    ]
