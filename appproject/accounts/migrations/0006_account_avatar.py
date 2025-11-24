# Generated migration file for avatar field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_group_groupmember_remove_account_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/', verbose_name='アバター画像'),
        ),
        # AddField(account_type) 操作を削除（既存列重複エラー回避）
    ]
