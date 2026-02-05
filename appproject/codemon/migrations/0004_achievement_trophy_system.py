# Generated migration for Achievement trophy system

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('codemon', '0003_accessory_image_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Achievementモデルの拡張
        migrations.AddField(
            model_name='achievement',
            name='category',
            field=models.CharField(choices=[('system', 'システム作成'), ('algorithm', 'アルゴリズム作成'), ('login', 'ログイン'), ('consecutive_login', '連続ログイン'), ('ai_chat', 'AI会話')], default='system', max_length=20, verbose_name='カテゴリー'),
        ),
        migrations.AddField(
            model_name='achievement',
            name='tier',
            field=models.CharField(blank=True, choices=[('bronze', 'ブロンズ'), ('silver', 'シルバー'), ('gold', 'ゴールド'), ('diamond', 'ダイヤ'), ('platinum', 'プラチナ')], max_length=10, null=True, verbose_name='段階'),
        ),
        migrations.AddField(
            model_name='achievement',
            name='target_count',
            field=models.IntegerField(default=1, verbose_name='目標回数'),
        ),
        migrations.AddField(
            model_name='achievement',
            name='icon',
            field=models.CharField(default='🏆', max_length=10, verbose_name='アイコン'),
        ),
        migrations.AddField(
            model_name='achievement',
            name='display_order',
            field=models.IntegerField(default=0, verbose_name='表示順'),
        ),
        migrations.AlterField(
            model_name='achievement',
            name='description',
            field=models.TextField(blank=True, verbose_name='説明'),
        ),
        
        # UserAchievementモデルの拡張
        migrations.AddField(
            model_name='userachievement',
            name='current_count',
            field=models.IntegerField(default=0, verbose_name='現在のカウント'),
        ),
        migrations.AddField(
            model_name='userachievement',
            name='is_achieved',
            field=models.BooleanField(default=False, verbose_name='達成済み'),
        ),
        migrations.AddField(
            model_name='userachievement',
            name='is_rewarded',
            field=models.BooleanField(default=False, verbose_name='報酬受取済み'),
        ),
        migrations.AddField(
            model_name='userachievement',
            name='rewarded_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='報酬受取日時'),
        ),
        migrations.RenameField(
            model_name='userachievement',
            old_name='achieved_at',
            new_name='achieved_at',
        ),
        
        # UserStatsモデルの作成
        migrations.CreateModel(
            name='UserStats',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('total_systems', models.IntegerField(default=0, verbose_name='システム作成数')),
                ('total_algorithms', models.IntegerField(default=0, verbose_name='アルゴリズム作成数')),
                ('total_login_days', models.IntegerField(default=0, verbose_name='総ログイン日数')),
                ('consecutive_login_days', models.IntegerField(default=0, verbose_name='連続ログイン日数')),
                ('last_login_date', models.DateField(blank=True, null=True, verbose_name='最終ログイン日')),
                ('total_ai_chats', models.IntegerField(default=0, verbose_name='AI会話回数')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='stats', to='accounts.Account')),
            ],
            options={
                'verbose_name': 'ユーザー統計',
                'verbose_name_plural': 'ユーザー統計',
                'db_table': 'user_stats',
            },
        ),
        
        # Achievementモデルのordering変更
        migrations.AlterModelOptions(
            name='achievement',
            options={'ordering': ['display_order', 'category', 'target_count'], 'verbose_name': '実績', 'verbose_name_plural': '実績'},
        ),
    ]
