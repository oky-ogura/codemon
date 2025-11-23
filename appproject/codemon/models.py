from django.db import models
from accounts.models import Account
from django.conf import settings
from django.utils import timezone


class System(models.Model):
    # system_id は PostgreSQL のシーケンスで管理（4000001 から開始）
    system_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='ユーザーID')
    system_name = models.CharField(max_length=100, verbose_name='システム名')
    system_description = models.TextField(blank=True, null=True, verbose_name='システム詳細')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        db_table = 'system'
        verbose_name = 'システム'
        verbose_name_plural = 'システム'

    def __str__(self):
        return f"{self.system_name} (ID: {self.system_id})"


class SystemElement(models.Model):
    # element_id は PostgreSQL のシーケンスで管理（7000001 から開始）
    element_id = models.BigAutoField(primary_key=True)
    system = models.ForeignKey(System, on_delete=models.CASCADE, related_name='elements', verbose_name='システムID')
    element_type = models.CharField(max_length=50, verbose_name='要素タイプ')
    element_label = models.CharField(max_length=200, blank=True, null=True, verbose_name='要素ラベル')
    element_value = models.TextField(blank=True, null=True, verbose_name='要素値')
    position_x = models.IntegerField(default=0, verbose_name='X座標')
    position_y = models.IntegerField(default=0, verbose_name='Y座標')
    width = models.IntegerField(blank=True, null=True, verbose_name='幅')
    height = models.IntegerField(blank=True, null=True, verbose_name='高さ')
    style_data = models.JSONField(blank=True, null=True, verbose_name='スタイルデータ')
    element_config = models.JSONField(blank=True, null=True, verbose_name='要素設定')
    sort_order = models.IntegerField(default=0, verbose_name='表示順')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        db_table = 'system_element'
        verbose_name = 'システム要素'
        verbose_name_plural = 'システム要素'
        ordering = ['sort_order', 'element_id']

    def __str__(self):
        return f"{self.element_type}: {self.element_label or 'No Label'} (ID: {self.element_id})"


class Algorithm(models.Model):
    # algorithm_id は PostgreSQL のシーケンスで管理（5000001 から開始）
    algorithm_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='ユーザーID')
    algorithm_name = models.CharField(max_length=100, verbose_name='アルゴリズム名')
    algorithm_description = models.TextField(blank=True, null=True, verbose_name='アルゴリズム概要')
    blockly_xml = models.TextField(blank=True, null=True, verbose_name='Blockly XML')
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
    user = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='ユーザーID')
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




class ChatThread(models.Model):
    """投函ボックス / スレッド - 教師が作成して生徒が投稿する用途を想定"""
    thread_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200, verbose_name='スレッド名')
    description = models.TextField(blank=True, null=True, verbose_name='説明')
    created_by = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='作成者')
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
    sender = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='送信者')
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
    reader = models.ForeignKey(Account, on_delete=models.CASCADE)
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
    scorer = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='採点者')
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



class Group(models.Model):
    """グループ管理テーブル

    既存データベースはカラム名 `user_id` を作成者として使っているため、
    Django 側ではフィールド名を `owner` のまま使いつつ DB カラム名を
    `user_id` にマップする（互換性維持）。
    """
    group_id = models.BigAutoField(primary_key=True)
    group_name = models.CharField(max_length=50, verbose_name='グループ名')
    description = models.TextField(blank=True, null=True, verbose_name='グループ説明')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    is_active = models.BooleanField(default=True, verbose_name='アクティブフラグ')
    owner = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        db_column='user_id',
        verbose_name='作成者'
    )

    # Many-to-many through GroupMember
    members = models.ManyToManyField(
        Account,
        through='GroupMember',
        related_name='joined_groups'
    )

    class Meta:
        db_table = 'group'
        verbose_name = 'グループ'
        verbose_name_plural = 'グループ'

    def __str__(self):
        return f"{self.group_name} (ID: {self.group_id})"


class GroupMember(models.Model):
    ROLE_OWNER = 'owner'
    ROLE_TEACHER = 'teacher'
    ROLE_STUDENT = 'student'

    ROLE_CHOICES = [
        (ROLE_OWNER, 'オーナー'),
        (ROLE_TEACHER, '教師'),
        (ROLE_STUDENT, '学生'),
    ]

    id = models.BigAutoField(primary_key=True)
    role = models.CharField(max_length=50, blank=True, null=True, verbose_name='メンバーの役割')
    # created_at (DB column) を保持する
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at', verbose_name='追加日時')
    # DBの既存スキーマではカラム名が group_id / member_user_id になっているため db_column を指定
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='memberships',
        db_column='group_id',
        verbose_name='グループ'
    )
    member = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='group_memberships',
        db_column='member_user_id',
        verbose_name='メンバー(アカウント)'
    )

    class Meta:
        db_table = 'group_member'
        verbose_name = 'グループメンバー'
        verbose_name_plural = 'グループメンバー'
        unique_together = (('group', 'member'),)

    # このモデルは既存のスキーマに合わせてカラム名を指定しているため
    # マイグレーションを作成/適用する際は注意してください。

    def __str__(self):
        return f"{self.member} in {self.group} ({self.role})"

# --- AI 会話履歴 ---
class AIConversation(models.Model):
    user = models.ForeignKey(
        Account,
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
