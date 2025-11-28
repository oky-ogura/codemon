# Generated migration for adding group_id column

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_merge_20251126_1231'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='group_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='参加グループID'),
        ),
    ]
