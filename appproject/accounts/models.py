from django.db import models


class Account(models.Model):
    # user_id は PostgreSQL のシーケンスで管理（20000001 から開始）
    user_id = models.BigAutoField(primary_key=True)
    user_name = models.CharField(max_length=50, verbose_name='氏名')
    email = models.EmailField(max_length=100, unique=True, verbose_name='メールアドレス')
    password = models.CharField(max_length=255, verbose_name='パスワード')
    # 年齢を保存できるようにフィールドを追加
    age = models.IntegerField(blank=True, null=True, verbose_name='年齢')
    account_type = models.CharField(max_length=20, blank=True, null=True, verbose_name='アカウント種別')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='アバター画像')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='登録日時')
    
    # 互換性のために `type` プロパティを提供する
    @property
    def type(self):
        """互換用プロパティ: 既存コードで owner.type を参照しているため account_type を返す"""
        return self.account_type

    @type.setter
    def type(self, value):
        self.account_type = value
    

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

# 他アプリの既存モデル（codemon.models.Group / GroupMember）を参照する
# 重複したテーブル定義を避けるため、ここでは Proxy モデルを定義します。
# Proxy モデルは同じ DB テーブルを参照しますが、新しいテーブルを作成せず、
# accounts アプリ内で使いやすい名前空間を提供します。
try:
    from codemon.models import Group as CodemonGroup, GroupMember as CodemonGroupMember

    class Group(CodemonGroup):
        class Meta:
            proxy = True
            app_label = 'accounts'
            verbose_name = 'グループ'
            verbose_name_plural = 'グループ'

    class GroupMember(CodemonGroupMember):
        class Meta:
            proxy = True
            app_label = 'accounts'
            verbose_name = 'グループメンバー'
            verbose_name_plural = 'グループメンバー'
except Exception:
    # インポートに失敗した場合は何もしない（起動時の循環インポート回避）
    pass