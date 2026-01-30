# Generated migration for adding image support to Accessory model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codemon', '0002_achievement_usercoin_accessory_useraccessory_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='accessory',
            name='image_path',
            field=models.CharField(blank=True, help_text='例: accessories/flower_inu.png', max_length=255, null=True, verbose_name='画像パス'),
        ),
        migrations.AddField(
            model_name='accessory',
            name='use_image',
            field=models.BooleanField(default=False, help_text='TrueならCSS背景画像、FalseならCSS描画', verbose_name='画像を使用'),
        ),
        migrations.AlterField(
            model_name='accessory',
            name='css_class',
            field=models.CharField(help_text='例: flower.inu', max_length=100, verbose_name='CSSクラス名'),
        ),
    ]
