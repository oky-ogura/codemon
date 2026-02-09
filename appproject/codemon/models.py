from django.db import models
## Account参照は文字列で行う（循環依存回避）
from django.conf import settings
from django.utils import timezone


class TutorialProgress(models.Model):
    """チュートリアル進行状況を管理するモデル"""
    user = models.OneToOneField('accounts.Account', on_delete=models.CASCADE, verbose_name='ユーザー', related_name='tutorial_progress')
    has_logged_in = models.BooleanField(default=False, verbose_name='初回ログイン済み')
    step1_completed = models.BooleanField(default=False, verbose_name='STEP1完了（メイン→システム）')
    step2_completed = models.BooleanField(default=False, verbose_name='STEP2完了（システム→アルゴリズム）')
    step3_completed = models.BooleanField(default=False, verbose_name='STEP3完了（チェックリスト→トロフィー→ショップ）')
    all_tutorials_completed = models.BooleanField(default=False, verbose_name='全チュートリアル完了')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        db_table = 'tutorial_progress'
        verbose_name = 'チュートリアル進行状況'
        verbose_name_plural = 'チュートリアル進行状況'

    def __str__(self):
        return f"{self.user.user_name}のチュートリアル進行状況"

    def mark_step_completed(self, step_number):
        """指定されたステップを完了としてマーク"""
        if step_number == 1:
            self.step1_completed = True
        elif step_number == 2:
            self.step2_completed = True
        elif step_number == 3:
            self.step3_completed = True
        
        # 全てのステップが完了したかチェック
        if self.step1_completed and self.step2_completed and self.step3_completed:
            self.all_tutorials_completed = True
        
        self.save()


class Tutorial1Plus1Progress(models.Model):
    """「1+1=?」チュートリアル進行状況を管理するモデル"""
    user = models.OneToOneField('accounts.Account', on_delete=models.CASCADE, verbose_name='ユーザー', related_name='tutorial_1plus1_progress')
    current_step = models.IntegerField(default=0, verbose_name='現在のステップ（0～31）')
    is_completed = models.BooleanField(default=False, verbose_name='チュートリアル完了')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='開始日時')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完了日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        db_table = 'tutorial_1plus1_progress'
        verbose_name = '1+1チュートリアル進行状況'
        verbose_name_plural = '1+1チュートリアル進行状況'

    def __str__(self):
        return f"{self.user.user_name}の1+1チュートリアル進行状況 (ステップ{self.current_step}/31)"

    def mark_completed(self):
        """チュートリアルを完了としてマーク"""
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()

    def reset_progress(self):
        """進捗をリセット（最初からやり直し）"""
        self.current_step = 0
        self.is_completed = False
        self.completed_at = None
        self.save()

    def advance_to_step(self, step_number):
        """指定したステップに進む"""
        if 0 <= step_number <= 31:
            self.current_step = step_number
            if step_number == 31:
                self.mark_completed()
            else:
                self.save()


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


class Algorithm(models.Model):
    # algorithm_id は PostgreSQL のシーケンスで管理（5000001 から開始）
    algorithm_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, verbose_name='ユーザーID')
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
    user = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, verbose_name='ユーザーID')
    checklist_name = models.CharField(max_length=100, verbose_name='チェックリスト名')
    checklist_description = models.TextField(blank=True, null=True, verbose_name='チェックリスト概要')
    due_date = models.DateField(blank=True, null=True, verbose_name='期限')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    is_selected = models.BooleanField(default=False, verbose_name='選択フラグ')

    class Meta:
        db_table = 'checklist'
        verbose_name = 'チェックリスト'
        verbose_name_plural = 'チェックリスト'

    def __str__(self):
        return f"{self.checklist_name} (ID: {self.checklist_id})"
    
    def days_until_due(self):
        """期限までの残り日数を返す"""
        if not self.due_date:
            return None
        from datetime import date
        delta = self.due_date - date.today()
        return delta.days


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


class MessegeGroup(models.Model):
    """教師が作成・管理するメッセージグループ。メンバーはMessegeMemberを通じて管理。"""
    # group_id は PostgreSQL のシーケンスで管理（7000001 から開始）
    group_id = models.BigAutoField(primary_key=True)
    group_name = models.CharField(max_length=50, verbose_name='グループ名')
    description = models.TextField(blank=True, null=True, verbose_name='グループ説明')
    password = models.CharField(max_length=255, blank=True, null=True, verbose_name='グループパスワード')
    owner = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, null=True, blank=True)
    members = models.ManyToManyField('accounts.Account', through='MessegeMember', related_name='joined_messege_groups')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    is_active = models.BooleanField(default=True, verbose_name='アクティブフラグ')

    class Meta:
        db_table = 'messege_group'
        verbose_name = 'メッセージグループ'
        verbose_name_plural = 'メッセージグループ'

    def __str__(self):
        return f"{self.group_name} (ID: {self.group_id})"


class MessegeMember(models.Model):
    """メッセージグループのメンバーシップを管理。役割や参加日時も記録。"""
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey('MessegeGroup', on_delete=models.CASCADE, related_name='memberships')
    member = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='messege_memberships')
    role = models.CharField(max_length=20, choices=[
        ('owner', 'オーナー'),
        ('teacher', '教師'),
        ('student', '学生')
    ], default='student')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'messege_group_member'
        verbose_name = 'メッセージグループメンバー'
        verbose_name_plural = 'メッセージグループメンバー'
        unique_together = [['group', 'member']]

    def __str__(self):
        return f"{self.member.user_name} in {self.group.group_name} ({self.role})"


class MessegeGroupInvite(models.Model):
    """メッセージグループ招待リンク"""
    invite_id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey('MessegeGroup', on_delete=models.CASCADE, related_name='invites')
    invited_email = models.EmailField(max_length=255)
    invited_by = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='messege_invites_sent')
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'messege_group_invite'
        verbose_name = 'メッセージグループ招待'
        verbose_name_plural = 'メッセージグループ招待'

    def __str__(self):
        return f"Invite {self.invite_id} for {self.invited_email}"


class DirectMessageThread(models.Model):
    """個別チャット（メールアドレス単位のスレッド）"""
    thread_id = models.BigAutoField(primary_key=True)
    owner = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='direct_threads_owned')
    participant_email = models.EmailField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'direct_message_thread'
        verbose_name = '個別チャットスレッド'
        verbose_name_plural = '個別チャットスレッド'
        unique_together = [['owner', 'participant_email']]

    def __str__(self):
        return f"DM {self.thread_id} ({self.participant_email})"


class DirectMessage(models.Model):
    """個別チャットメッセージ"""
    message_id = models.BigAutoField(primary_key=True)
    thread = models.ForeignKey('DirectMessageThread', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('accounts.Account', on_delete=models.SET_NULL, null=True, blank=True)
    sender_label = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'direct_message'
        verbose_name = '個別チャットメッセージ'
        verbose_name_plural = '個別チャットメッセージ'
        ordering = ['created_at']

    def __str__(self):
        return f"DM message {self.message_id}"


class ChatThread(models.Model):
    """投函ボックス / スレッド - 教師が作成して生徒が投稿する用途を想定"""
    thread_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200, verbose_name='スレッド名')
    description = models.TextField(blank=True, null=True, verbose_name='説明')
    created_by = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, verbose_name='作成者')
    group = models.ForeignKey('MessegeGroup', on_delete=models.CASCADE, null=True, blank=True, related_name='threads', verbose_name='メッセージグループ')
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
    good_points = models.TextField(blank=True, null=True, verbose_name='良かったこと')
    improvement_points = models.TextField(blank=True, null=True, verbose_name='惜しかったこと')
    advice = models.TextField(blank=True, null=True, verbose_name='まとめ・アドバイス')
    is_checked = models.BooleanField(default=False, verbose_name='採点済みチェック')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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


# --- ユーザーコイン・実績システム ---
class UserCoin(models.Model):
    """ユーザーの所持コイン"""
    user = models.OneToOneField(
        'accounts.Account',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='coin_balance'
    )
    balance = models.IntegerField(default=0, verbose_name='コイン残高')
    total_earned = models.IntegerField(default=0, verbose_name='累計獲得コイン')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        db_table = 'user_coin'
        verbose_name = 'ユーザーコイン'
        verbose_name_plural = 'ユーザーコイン'

    def __str__(self):
        return f"{self.user.user_name}: {self.balance}コイン"


class Achievement(models.Model):
    """実績マスターデータ"""
    TIER_CHOICES = [
        ('bronze', 'ブロンズ'),
        ('silver', 'シルバー'),
        ('gold', 'ゴールド'),
        ('diamond', 'ダイヤ'),
        ('platinum', 'プラチナ'),
    ]
    
    CATEGORY_CHOICES = [
        ('system', 'システム作成'),
        ('algorithm', 'アルゴリズム作成'),
        ('login', 'ログイン'),
        ('consecutive_login', '連続ログイン'),
        ('ai_chat', 'AI会話'),
        ('ai_chat_consecutive', 'AI連続会話'),
        ('checklist_create', 'チェックリスト作成'),
        ('checklist_complete', 'チェックリスト完了'),
        ('accessory', 'アクセサリー'),
    ]
    
    achievement_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='実績名')
    description = models.TextField(verbose_name='説明', blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='カテゴリー', default='system')
    tier = models.CharField(max_length=10, choices=TIER_CHOICES, verbose_name='段階', blank=True, null=True)
    target_count = models.IntegerField(verbose_name='目標回数', default=1)
    reward_coins = models.IntegerField(verbose_name='報酬コイン')
    icon = models.CharField(max_length=10, default='🏆', verbose_name='アイコン')
    display_order = models.IntegerField(default=0, verbose_name='表示順')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')

    class Meta:
        db_table = 'achievement'
        verbose_name = '実績'
        verbose_name_plural = '実績'
        ordering = ['display_order', 'category', 'target_count']

    def __str__(self):
        tier_display = f" ({self.get_tier_display()})" if self.tier else ""
        return f"{self.name}{tier_display}"


class UserAchievement(models.Model):
    """ユーザーの実績達成状況"""
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='user_achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    current_count = models.IntegerField(default=0, verbose_name='現在のカウント')
    is_achieved = models.BooleanField(default=False, verbose_name='達成済み')
    is_rewarded = models.BooleanField(default=False, verbose_name='報酬受取済み')
    achieved_at = models.DateTimeField(null=True, blank=True, verbose_name='達成日時')
    rewarded_at = models.DateTimeField(null=True, blank=True, verbose_name='報酬受取日時')

    class Meta:
        db_table = 'user_achievement'
        verbose_name = 'ユーザー実績'
        verbose_name_plural = 'ユーザー実績'
        unique_together = [['user', 'achievement']]

    def __str__(self):
        status = "達成済み" if self.is_achieved else f"{self.current_count}/{self.achievement.target_count}"
        return f"{self.user.user_name} - {self.achievement.name} ({status})"


class UserStats(models.Model):
    """ユーザーの統計情報"""
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField('accounts.Account', on_delete=models.CASCADE, related_name='stats')
    total_systems = models.IntegerField(default=0, verbose_name='システム作成数')
    total_algorithms = models.IntegerField(default=0, verbose_name='アルゴリズム作成数')
    total_login_days = models.IntegerField(default=0, verbose_name='総ログイン日数')
    consecutive_login_days = models.IntegerField(default=0, verbose_name='連続ログイン日数')
    last_login_date = models.DateField(null=True, blank=True, verbose_name='最終ログイン日')
    total_ai_chats = models.IntegerField(default=0, verbose_name='AI会話回数')
    consecutive_ai_chat_days = models.IntegerField(default=0, verbose_name='連続AI会話日数')
    last_ai_chat_date = models.DateField(null=True, blank=True, verbose_name='最終AI会話日')
    total_checklists_created = models.IntegerField(default=0, verbose_name='作成チェックリスト数')
    total_checklist_items_completed = models.IntegerField(default=0, verbose_name='完了チェック項目数')
    total_accessories_purchased = models.IntegerField(default=0, verbose_name='購入アクセサリー数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        db_table = 'user_stats'
        verbose_name = 'ユーザー統計'
        verbose_name_plural = 'ユーザー統計'

    def __str__(self):
        return f"{self.user.user_name} の統計"


# --- アクセサリーシステム ---
class Accessory(models.Model):
    """アクセサリーマスターデータ"""
    CATEGORY_CHOICES = [
        ('flower', '花'),
        ('glasses', '眼鏡'),
        ('hat', '帽子'),
        ('star', '星'),
        ('crown', '王冠'),
        ('ribbon', 'リボン'),
        ('other', 'その他'),
    ]
    
    accessory_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='アクセサリー名')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name='カテゴリ')
    css_class = models.CharField(max_length=100, verbose_name='CSSクラス名', help_text='例: flower.inu')
    image_path = models.CharField(max_length=255, blank=True, null=True, verbose_name='画像パス', help_text='例: accessories/flower_inu.png')
    use_image = models.BooleanField(default=False, verbose_name='画像を使用', help_text='TrueならCSS背景画像、FalseならCSS描画')
    description = models.TextField(blank=True, null=True, verbose_name='説明')
    
    # 解放条件（どちらか片方を設定）
    unlock_coins = models.IntegerField(default=0, verbose_name='必要コイン数')
    unlock_achievement = models.ForeignKey(
        Achievement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='必要実績'
    )
    
    # 小アイコン用の簡略表示設定
    simple_style = models.JSONField(
        blank=True,
        null=True,
        verbose_name='簡略表示スタイル',
        help_text='小アイコン用のCSS設定（JSON形式）'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')

    class Meta:
        db_table = 'accessory'
        verbose_name = 'アクセサリー'
        verbose_name_plural = 'アクセサリー'

    def __str__(self):
        return self.name


class UserAccessory(models.Model):
    """ユーザーの所持アクセサリー"""
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='owned_accessories')
    accessory = models.ForeignKey(Accessory, on_delete=models.CASCADE)
    is_equipped = models.BooleanField(default=False, verbose_name='装備中')
    obtained_at = models.DateTimeField(auto_now_add=True, verbose_name='取得日時')

    class Meta:
        db_table = 'user_accessory'
        verbose_name = 'ユーザーアクセサリー'
        verbose_name_plural = 'ユーザーアクセサリー'
        unique_together = [['user', 'accessory']]

    def __str__(self):
        equipped = " [装備中]" if self.is_equipped else ""
        return f"{self.user.user_name} - {self.accessory.name}{equipped}"
