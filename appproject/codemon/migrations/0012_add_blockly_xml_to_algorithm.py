# Generated manually to add blockly_xml column to algorithm table

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codemon', '0011_auto_create_accessories'),
    ]

    operations = [
        migrations.AddField(
            model_name='algorithm',
            name='blockly_xml',
            field=models.TextField(blank=True, null=True, verbose_name='Blockly XML'),
        ),
    ]
