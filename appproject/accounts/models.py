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
    group_id = models.IntegerField(blank=True, null=True, verbose_name='グループID')
    
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

# accounts側のグループ（group）
class Group(models.Model):
    """accountsアプリで作成・管理するグループ"""
    group_id = models.BigAutoField(primary_key=True)
    group_name = models.CharField(max_length=50, verbose_name='グループ名')
    description = models.TextField(blank=True, null=True, verbose_name='グループ説明')
    password = models.CharField(max_length=255, blank=True, null=True, verbose_name='グループパスワード')
    owner = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, null=True, blank=True)
    members = models.ManyToManyField('accounts.Account', through='GroupMember', related_name='joined_groups')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    is_active = models.BooleanField(default=True, verbose_name='アクティブフラグ')

    class Meta:
        db_table = 'group'
        verbose_name = 'グループ'
        verbose_name_plural = 'グループ'

    def __str__(self):
        return f"{self.group_name} (ID: {self.group_id})"


class GroupMember(models.Model):
    """accounts側グループのメンバーシップ"""
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='memberships')
    member = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='group_memberships')
    role = models.CharField(max_length=20, choices=[
        ('owner', 'オーナー'),
        ('teacher', '教師'),
        ('student', '学生')
    ], default='student')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'group_member'
        verbose_name = 'グループメンバー'
        verbose_name_plural = 'グループメンバー'
        unique_together = [['group', 'member']]

    def __str__(self):
        return f"{self.member.user_name} in {self.group.group_name} ({self.role})"