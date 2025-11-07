from django.db import models


class Account(models.Model):
    # user_id は PostgreSQL のシーケンスで管理（20000001 から開始）
    user_id = models.BigAutoField(primary_key=True)
    user_name = models.CharField(max_length=50, verbose_name='氏名')
    email = models.EmailField(max_length=100, unique=True, verbose_name='メールアドレス')
    password = models.CharField(max_length=255, verbose_name='パスワード')
    account_type = models.CharField(max_length=20, blank=True, null=True, verbose_name='アカウント種別')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='登録日時')
    type = models.CharField(max_length=50, blank=True, null=True, verbose_name='種別')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='アバター画像')

    class Meta:
        db_table = 'account'
        verbose_name = 'アカウント'
        verbose_name_plural = 'アカウント'

    def __str__(self):
        return f"{self.user_name} <{self.email}>"


class AiConfig(models.Model):
    # ai_setting_id は PostgreSQL のシーケンスで管理（3000001 から開始）
    ai_setting_id = models.BigAutoField(primary_key=True)
    user_id = models.IntegerField(verbose_name='ユーザーID')
    appearance = models.CharField(max_length=100, default='三角', verbose_name='AI外見')
    ai_name = models.CharField(max_length=50, default='codemon', verbose_name='AI名前')
    ai_personality = models.CharField(max_length=100, blank=True, null=True, default='元気', verbose_name='AI性格')
    ai_speech = models.CharField(max_length=50, blank=True, null=True, default='です', verbose_name='AI語尾')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')

    class Meta:
        db_table = 'ai_config'
        verbose_name = 'AI設定'
        verbose_name_plural = 'AI設定'

    def __str__(self):
        return f"AI設定 {self.ai_setting_id} - {self.ai_name}"
