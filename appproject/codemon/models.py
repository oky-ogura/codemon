from django.db import models
## Account参照は文字列で行う（循環依存回避）
from django.conf import settings
from django.utils import timezone


class System(models.Model):
    # system_id は PostgreSQL のシーケンスで管理（4000001 から開始）
    system_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, verbose_name='ユーザーID')
    system_name = models.CharField(max_length=100, verbose_name='システム名')
    system_description = models.TextField(blank=True, null=True, verbose_name='システム種類')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        db_table = 'system'
        verbose_name = 'システム'
        verbose_name_plural = 'システム'

    def __str__(self):
        return f"{self.system_name} (ID: {self.system_id})"


class Algorithm(models.Model):
    # algorithm_id は PostgreSQL のシーケンスで管理（5000001 から開始）
    algorithm_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, verbose_name='ユーザーID')
    algorithm_name = models.CharField(max_length=100, verbose_name='アルゴリズム名')
    algorithm_description = models.TextField(blank=True, null=True, verbose_name='アルゴリズム概要')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        db_table = 'algorithm'
        verbose_name = 'アルゴリズム'
        verbose_name_plural = 'アルゴリズム'

    def __str__(self):
        return f"{self.algorithm_name} (ID: {self.algorithm_id})"


class Checklist(models.Model):
    # checklist_id は PostgreSQL のシーケンスで管理（6000001 から開始）
    checklist_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, verbose_name='ユーザーID')
    checklist_name = models.CharField(max_length=100, verbose_name='チェックリスト名')
    checklist_description = models.TextField(blank=True, null=True, verbose_name='チェックリスト概要')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    is_selected = models.BooleanField(default=False, verbose_name='選択フラグ')

    class Meta:
        db_table = 'checklist'
        verbose_name = 'チェックリスト'
        verbose_name_plural = 'チェックリスト'

    def __str__(self):
        return f"{self.checklist_name} (ID: {self.checklist_id})"


class ChecklistItem(models.Model):
    # checklist_item_id は PostgreSQL のシーケンスで管理（6001001 から開始）
    checklist_item_id = models.BigAutoField(primary_key=True)
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, related_name='items', verbose_name='チェックリストID')
    item_text = models.TextField(verbose_name='項目テキスト')
    is_done = models.BooleanField(default=False, verbose_name='完了フラグ')
    sort_order = models.IntegerField(default=0, verbose_name='表示順')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        db_table = 'checklist_item'
        verbose_name = 'チェックリスト項目'
        verbose_name_plural = 'チェックリスト項目'
        ordering = ['sort_order', 'checklist_item_id']

    def __str__(self):
        return f"{self.item_text[:40]}{'...' if len(self.item_text) > 40 else ''} (ID: {self.checklist_item_id})"


class Group(models.Model):
    """教師が作成・管理するグループ。メンバーはGroupMemberを通じて管理。"""
    # group_id は PostgreSQL のシーケンスで管理（7000001 から開始）
    group_id = models.BigAutoField(primary_key=True)
    group_name = models.CharField(max_length=50, verbose_name='グループ名')
    description = models.TextField(blank=True, null=True, verbose_name='グループ説明')
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
    """グループのメンバーシップを管理。役割や参加日時も記録。"""
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


class ChatThread(models.Model):
    """投函ボックス / スレッド - 教師が作成して生徒が投稿する用途を想定"""
    thread_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200, verbose_name='スレッド名')
    description = models.TextField(blank=True, null=True, verbose_name='説明')
    created_by = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, verbose_name='作成者')
    group = models.ForeignKey('Group', on_delete=models.CASCADE, null=True, blank=True, related_name='threads', verbose_name='グループ')
    is_active = models.BooleanField(default=True, verbose_name='アクティブフラグ')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')

    class Meta:
        db_table = 'chat_thread'
        verbose_name = 'チャットスレッド'
        verbose_name_plural = 'チャットスレッド'

    def __str__(self):
        return f"{self.title} (ID: {self.thread_id})"


class ChatMessage(models.Model):
    """チャットメッセージ。AI を含む送信者は Account を参照。"""
    message_id = models.BigAutoField(primary_key=True)
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, verbose_name='送信者')
    content = models.TextField(blank=True, null=True, verbose_name='メッセージ本文')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='送信日時')
    is_deleted = models.BooleanField(default=False, verbose_name='削除フラグ')

    class Meta:
        db_table = 'chat_message'
        verbose_name = 'チャットメッセージ'
        verbose_name_plural = 'チャットメッセージ'
        ordering = ['created_at']

    def __str__(self):
        return f"{(self.content or '')[:40]}{'...' if self.content and len(self.content) > 40 else ''} (ID: {self.message_id})"


class ChatAttachment(models.Model):
    """メッセージに紐づくファイル/画像の保存参照"""
    attachment_id = models.BigAutoField(primary_key=True)
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='chat_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_attachment'
        verbose_name = 'チャット添付'
        verbose_name_plural = 'チャット添付'

    def __str__(self):
        return f"Attachment {self.attachment_id} for message {self.message.message_id}"


class ReadReceipt(models.Model):
    """既読管理。メッセージごとに誰が読んだかを記録する。"""
    id = models.BigAutoField(primary_key=True)
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='read_receipts')
    reader = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_read_receipt'
        verbose_name = '既読レシート'
        verbose_name_plural = '既読レシート'


class ChatScore(models.Model):
    """教師が付ける点数（デフォルトはメッセージ単位）。必要に応じてスレッド単位の拡張も可能。"""
    id = models.BigAutoField(primary_key=True)
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='scores', null=True, blank=True)
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name='scores', null=True, blank=True)
    scorer = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, verbose_name='採点者')
    score = models.IntegerField(null=True, blank=True)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_score'
        verbose_name = 'チャットスコア'
        verbose_name_plural = 'チャットスコア'

    def __str__(self):
        target = f"message {self.message.message_id}" if self.message else f"thread {self.thread.thread_id}"
        return f"Score {self.score} by {self.scorer} for {target}"


# --- AI 会話履歴 ---
class AIConversation(models.Model):
    user = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name="ai_conversations",
    )
    character_id = models.CharField(max_length=32, default="usagi")
    title = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user_id}:{self.character_id}:{self.created_at:%Y%m%d}"


class AIMessage(models.Model):
    ROLE_CHOICES = (("user", "User"), ("assistant", "Assistant"), ("system", "System"))
    conversation = models.ForeignKey(
        AIConversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    content = models.TextField()
    tokens = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}@{self.created_at:%H:%M:%S}"
