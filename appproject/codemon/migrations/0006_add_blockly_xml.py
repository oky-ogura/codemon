from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codemon', '0005_merge_20251113_0945'),
    ]

    operations = [
        migrations.AddField(
            model_name='algorithm',
            name='blockly_xml',
            field=models.TextField(blank=True, null=True, verbose_name='Blockly XML'),
        ),
    ]