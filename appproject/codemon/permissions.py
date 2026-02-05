"""
権限制御モジュール
"""
from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .models import ChatThread, ChatMessage, MessegeGroup, MessegeMember

# 互換用エイリアス（chat側のメッセージグループをGroup名で扱う既存コード向け）
Group = MessegeGroup
GroupMember = MessegeMember

def teacher_required(view_func):
    """教師権限が必要なビューのデコレーター"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'type') or request.user.type != 'teacher':
            messages.error(request, '教師権限が必要です')
            return redirect('accounts:student_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def can_access_thread(user, thread):
    """スレッドへのアクセス権限をチェック"""
    if not user or not hasattr(user, 'type'):
        return False

    # 教師は作成者であれば全てのスレッドにアクセス可能
    if user.type == 'teacher' and thread.created_by == user:
        return True

    # グループに紐づくスレッドの場合、メンバーシップをチェック
    if thread.group:
        return GroupMember.objects.filter(
            group=thread.group,
            member=user,
            is_active=True
        ).exists()

    # グループなしのスレッドは教師のみアクセス可能
    return user.type == 'teacher'

def can_modify_message(user, message):
    """メッセージの編集/削除権限をチェック"""
    if not user or not hasattr(user, 'type'):
        return False

    # 教師は全てのメッセージを編集/削除可能
    if user.type == 'teacher':
        return True

    # 送信者本人は自分のメッセージを編集/削除可能
    return message.sender == user

def can_manage_group(user, group):
    """グループの管理権限をチェック"""
    if not user or not hasattr(user, 'type'):
        return False

    # グループのオーナーのみが管理可能
    return user.type == 'teacher' and group.owner == user