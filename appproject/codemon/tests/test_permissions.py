"""
権限制御のテストケース
"""
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from accounts.models import Account
from codemon.models import (
    ChatThread, ChatMessage, ReadReceipt, ChatScore,
    Group, GroupMember
)

class PermissionsTest(TestCase):
    def setUp(self):
        """テスト用のデータを作成"""
        # 教師アカウントの作成
        self.teacher = Account.objects.create(
            email='teacher@example.com',
            user_name='テスト教師',
            type='teacher',
            password='password123'
        )

        # 学生アカウントの作成
        self.student = Account.objects.create(
            email='student@example.com',
            user_name='テスト学生',
            type='student',
            password='password123'
        )

        # グループの作成
        self.group = Group.objects.create(
            group_name='テストグループ',
            owner=self.teacher
        )

        # グループメンバーシップの作成
        GroupMember.objects.create(
            group=self.group,
            member=self.student,
            role='student'
        )

        # スレッドの作成（グループあり）
        self.thread = ChatThread.objects.create(
            title='テストスレッド',
            created_by=self.teacher,
            group=self.group
        )

        # メッセージの作成
        self.message = ChatMessage.objects.create(
            thread=self.thread,
            sender=self.student,
            content='テストメッセージ'
        )

    def test_thread_access_permissions(self):
        """スレッドへのアクセス権限テスト"""
        # 未ログインの場合リダイレクト
        response = self.client.get(reverse('codemon:thread_detail', args=[self.thread.thread_id]))
        self.assertEqual(response.status_code, 302)

        # 教師でログイン
        self.client.force_login(self.teacher)
        response = self.client.get(reverse('codemon:thread_detail', args=[self.thread.thread_id]))
        self.assertEqual(response.status_code, 200)

        # 学生でログイン（グループメンバー）
        self.client.force_login(self.student)
        response = self.client.get(reverse('codemon:thread_detail', args=[self.thread.thread_id]))
        self.assertEqual(response.status_code, 200)

        # グループメンバーでない学生を作成
        other_student = Account.objects.create(
            email='other@example.com',
            user_name='別の学生',
            type='student',
            password='password123'
        )
        self.client.force_login(other_student)
        response = self.client.get(reverse('codemon:thread_detail', args=[self.thread.thread_id]))
        self.assertEqual(response.status_code, 403)  # アクセス拒否

    def test_message_modification_permissions(self):
        """メッセージの編集/削除権限テスト"""
        # 未ログインの場合
        response = self.client.post(reverse('codemon:delete_message', args=[self.message.message_id]))
        self.assertEqual(response.status_code, 403)

        # 送信者本人の場合
        self.client.force_login(self.student)
        response = self.client.post(reverse('codemon:delete_message', args=[self.message.message_id]))
        self.assertEqual(response.status_code, 200)

        # メッセージが削除されたことを確認
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_deleted)

        # 別の学生の場合
        other_student = Account.objects.create(
            email='other@example.com',
            user_name='別の学生',
            type='student',
            password='password123'
        )
        self.client.force_login(other_student)
        response = self.client.post(reverse('codemon:delete_message', args=[self.message.message_id]))
        self.assertEqual(response.status_code, 403)

    def test_group_management_permissions(self):
        """グループ管理権限テスト"""
        group_data = {
            'group_name': '新規グループ',
            'description': 'テスト用グループ'
        }

        # 未ログインの場合
        response = self.client.post(reverse('codemon:group_create'), group_data)
        self.assertEqual(response.status_code, 302)  # ログインページへリダイレクト

        # 学生の場合
        self.client.force_login(self.student)
        response = self.client.post(reverse('codemon:group_create'), group_data)
        self.assertEqual(response.status_code, 302)  # アクセス拒否

        # 教師の場合
        self.client.force_login(self.teacher)
        response = self.client.post(reverse('codemon:group_create'), group_data)
        self.assertEqual(response.status_code, 302)  # 成功して詳細ページへリダイレクト

        # グループが作成されたことを確認
        self.assertTrue(Group.objects.filter(group_name='新規グループ').exists())

    def test_read_receipt_functionality(self):
        """既読機能のテスト"""
        # 学生がメッセージを既読にする
        self.client.force_login(self.student)
        ReadReceipt.objects.create(
            message=self.message,
            reader=self.student
        )

        # 教師が既読者一覧を取得
        self.client.force_login(self.teacher)
        response = self.client.get(reverse('codemon:thread_readers', args=[self.thread.thread_id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.student.user_name, str(response.content))