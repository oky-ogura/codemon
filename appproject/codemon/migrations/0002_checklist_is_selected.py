from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('codemon', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='checklist',
            name='is_selected',
            field=models.BooleanField(default=False, verbose_name='選択フラグ'),
        ),
    ]