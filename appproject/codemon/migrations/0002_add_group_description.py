from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("codemon", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='グループ説明'),
        ),
    ]
