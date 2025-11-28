import os
import json
from functools import wraps
from django.shortcuts import render, get_object_or_404, redirect
from django.db import models
from django.db import transaction
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required as _login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseForbidden, FileResponse
from django.urls import reverse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .permissions import teacher_required, can_access_thread, can_modify_message
from .models import (
    Checklist, ChecklistItem, ChatThread, ChatScore, ChatMessage, ChatAttachment,
    Group, GroupMember, AIConversation, AIMessage, System, Algorithm
)
from accounts.models import Account
from django.utils import timezone
from django.db.models import Q

# カスタムログイン必須デコレータ（セッションベース認証用）
def session_login_required(view_func):
	"""
	セッションベースの認証をチェックするデコレータ。
	request.session['is_account_authenticated'] が True でない場合、
	ログインページにリダイレクトします。
	"""
	@wraps(view_func)
	def _wrapped_view(request, *args, **kwargs):
		# デバッグ出力
		print(f"DEBUG decorator: session_key = {request.session.session_key}")
		print(f"DEBUG decorator: session data = {dict(request.session)}")
		print(f"DEBUG decorator: is_account_authenticated = {request.session.get('is_account_authenticated')}")
		
		if not request.session.get('is_account_authenticated'):
			from django.urls import reverse
			login_url = reverse('accounts:student_login')
			next_url = request.get_full_path()
			print(f"DEBUG decorator: Redirecting to {login_url}?next={next_url}")
			return redirect(f'{login_url}?next={next_url}')
		return view_func(request, *args, **kwargs)
	return _wrapped_view

# When ALLOW_ANONYMOUS_VIEWS is True (development convenience), make
# login_required a no-op so pages can be opened without logging in.
if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
	def login_required(fn):
		return fn
else:
	login_required = session_login_required  # カスタムデコレータを使用


def _get_write_owner(request):
    """Return an Account instance for writes.
    If user is authenticated, return that Account-like object. If anonymous and
    ALLOW_ANONYMOUS_VIEWS is True, return or create a dev Account.
    Otherwise return None.
    """
    # If Django auth is present, try to return the linked Account
    if getattr(request, 'user', None) and getattr(request.user, 'is_authenticated', False):
        try:
            acct = Account.objects.get(user=request.user)
            return acct
        except Account.DoesNotExist:
            # fall back to Django user object
            return request.user

    # Support custom session auth used elsewhere in this project
    if request.session.get('is_account_authenticated'):
        _account_user_id = request.session.get('account_user_id')
        if _account_user_id:
            try:
                acct = Account.objects.get(user_id=_account_user_id)
                return acct
            except Account.DoesNotExist:
                return None

    # Dev convenience: return or create a dev anonymous Account
    if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
        acct, _ = Account.objects.get_or_create(
            email='dev_anonymous@local',
            defaults={
                'user_name': '開発用匿名',
                'password': 'dev',
                'account_type': 'dev',
                'age': 0,
            }
        )
        return acct

    return None


@login_required
def systems_list(request):
    owner = _get_write_owner(request)
    if owner is None:
        return redirect('accounts:student_login')
    systems = System.objects.filter(user=owner).order_by('-updated_at')
    # デバッグ: セッション情報をコンソールに出力
    print(f"DEBUG systems_list: session keys = {list(request.session.keys())}")
    print(f"DEBUG systems_list: is_account_authenticated = {request.session.get('is_account_authenticated')}")
    return render(request, 'codemon/systems_list.html', {'systems': systems})


@login_required
def algorithms_list(request):
    owner = _get_write_owner(request)
    if owner is None:
        return redirect('accounts:student_login')
    algorithms = Algorithm.objects.filter(user=owner).order_by('-updated_at')
    return render(request, 'codemon/algorithms_list.html', {'algorithms': algorithms})


def chat_view(request):
    # Chat page: prepare sidebar data (groups + their threads) and optionally
    # an initial selected thread if provided via GET param.
    owner = _get_write_owner(request)
    groups_with_threads = []
    ungrouped_threads = []
    selected_thread_id = request.GET.get('thread_id')
    initial_messages = []

    if owner is not None:
        # Teacher: threads created by owner; Student: threads in member groups
        if getattr(owner, 'type', '') == 'teacher':
            groups = Group.objects.filter(owner=owner, is_active=True)
            for g in groups:
                threads = ChatThread.objects.filter(group=g, is_active=True).order_by('-created_at')
                groups_with_threads.append({'group': g, 'threads': threads})
            # ungrouped threads created by this teacher
            ungrouped_threads = ChatThread.objects.filter(group__isnull=True, created_by=owner, is_active=True).order_by('-created_at')
        else:
            # student: groups where member
            member_group_ids = GroupMember.objects.filter(member=owner).values_list('group_id', flat=True)
            groups = Group.objects.filter(group_id__in=member_group_ids, is_active=True)
            for g in groups:
                threads = ChatThread.objects.filter(group=g, is_active=True).order_by('-created_at')
                groups_with_threads.append({'group': g, 'threads': threads})
            # also threads without group that the owner created
            ungrouped_threads = ChatThread.objects.filter(group__isnull=True, created_by=owner, is_active=True).order_by('-created_at')

        # If an initial thread was requested, load its recent messages
        if selected_thread_id:
            try:
                st = ChatThread.objects.get(thread_id=selected_thread_id, is_active=True)
                # Access control: reuse can_access_thread utility
                if can_access_thread(owner, st):
                    msgs = st.messages.filter(is_deleted=False).select_related('sender').order_by('created_at')[:200]
                    for m in msgs:
                        initial_messages.append({
                            'id': m.message_id,
                            'content': m.content,
                            'user_id': getattr(m.sender, 'user_id', None),
                            'username': getattr(m.sender, 'user_name', ''),
                            'created_at': m.created_at.isoformat(),
                            'attachments': [
                                {'id': a.attachment_id, 'url': a.file.url, 'filename': os.path.basename(a.file.name)}
                                for a in m.attachments.all()
                            ]
                        })
            except Exception:
                selected_thread_id = None

    # Render chat template with sidebar data and optionally initial messages
    return render(request, 'codemon/chat.html', {
        'groups_with_threads': groups_with_threads,
        'ungrouped_threads': ungrouped_threads,
        'selected_thread_id': selected_thread_id,
        'initial_messages': initial_messages,
        'initial_messages_json': json.dumps(initial_messages),
    })


def thread_list(request):
    """投函ボックス（スレッド）一覧。教師は作成したスレッド、学生は所属グループのスレッドを閲覧。"""
    owner = _get_write_owner(request)
    if owner is None:
        return redirect('accounts:student_login')

    if getattr(owner, 'type', '') == 'teacher':
        threads = ChatThread.objects.filter(created_by=owner, is_active=True).order_by('-created_at')
    else:
        # 学生は所属グループに紐づくスレッドを閲覧
        threads = ChatThread.objects.filter(group__memberships__member=owner, is_active=True).distinct().order_by('-created_at')

    return render(request, 'codemon/thread_list.html', {'threads': threads, 'is_teacher': owner.type == 'teacher'})


def thread_create(request):
    """スレッド作成（教師のみ）。グループ指定可能。"""
    owner = _get_write_owner(request)
    if owner is None or getattr(owner, 'type', '') != 'teacher':
        messages.error(request, 'スレッドの作成には教師権限が必要です')
        return redirect('codemon:thread_list')

    groups = Group.objects.filter(owner=owner, is_active=True)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        group_id = request.POST.get('group_id')

        if not title:
            messages.error(request, 'スレッド名は必須です')
        else:
            thread = ChatThread.objects.create(
                title=title,
                description=description,
                created_by=owner,
                group_id=group_id if group_id else None
            )
            messages.success(request, f'スレッド「{title}」を作成しました')
            return redirect('codemon:thread_detail', thread_id=thread.thread_id)

    return render(request, 'codemon/thread_create.html', {'groups': groups})


def thread_detail(request, thread_id):
    """スレッド詳細（メッセージ一覧）"""
    owner = _get_write_owner(request)
    if owner is None:
        return redirect('accounts:student_login')

    thread = get_object_or_404(ChatThread, thread_id=thread_id, is_active=True)

    # アクセス権: 教師は作成者、学生はグループメンバーであること
    if getattr(owner, 'type', '') != 'teacher':
        if thread.group:
            if not GroupMember.objects.filter(group=thread.group, member=owner).exists():
                return HttpResponseForbidden('このスレッドにアクセスする権限がありません')

    messages_qs = thread.messages.filter(is_deleted=False).select_related('sender').order_by('created_at')
    return render(request, 'codemon/thread_detail.html', {'thread': thread, 'messages': messages_qs})


def thread_messages_api(request, thread_id):
    """Return JSON list of messages for the given thread_id.
    Used by the chat UI to fetch messages asynchronously.
    """
    owner = _get_write_owner(request)
    if owner is None:
        return JsonResponse({'error': 'authentication required'}, status=401)

    thread = get_object_or_404(ChatThread, thread_id=thread_id, is_active=True)

    # Access control: teacher or group member
    if not can_access_thread(owner, thread):
        return JsonResponse({'error': 'forbidden'}, status=403)

    msgs = thread.messages.filter(is_deleted=False).select_related('sender').order_by('created_at')
    out = []
    for m in msgs:
        out.append({
            'id': m.message_id,
            'content': m.content,
            'user_id': getattr(m.sender, 'user_id', None),
            'username': getattr(m.sender, 'user_name', ''),
            'created_at': m.created_at.isoformat(),
            'attachments': [
                {'id': a.attachment_id, 'url': a.file.url, 'filename': os.path.basename(a.file.name)}
                for a in m.attachments.all()
            ]
        })

    return JsonResponse({'thread_id': thread.thread_id, 'messages': out})


def thread_edit(request, thread_id):
    """スレッド編集（作成者の教師のみ）"""
    owner = _get_write_owner(request)
    if owner is None or getattr(owner, 'type', '') != 'teacher':
        messages.error(request, '権限がありません')
        return redirect('codemon:thread_list')

    thread = get_object_or_404(ChatThread, thread_id=thread_id, created_by=owner, is_active=True)
    groups = Group.objects.filter(owner=owner, is_active=True)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        group_id = request.POST.get('group_id')

        if not title:
            messages.error(request, 'スレッド名は必須です')
        else:
            thread.title = title
            thread.description = description
            thread.group_id = group_id if group_id else None
            thread.save()
            messages.success(request, 'スレッドを更新しました')
            return redirect('codemon:thread_detail', thread_id=thread.thread_id)

    return render(request, 'codemon/thread_edit.html', {'thread': thread, 'groups': groups})


@require_POST
def thread_delete(request, thread_id):
    """スレッド削除（論理削除）。作成者の教師のみ実行可能。"""
    owner = _get_write_owner(request)
    if owner is None or getattr(owner, 'type', '') != 'teacher':
        return HttpResponseForbidden('教師権限が必要です')

    thread = get_object_or_404(ChatThread, thread_id=thread_id, created_by=owner, is_active=True)
    thread.is_active = False
    thread.save()
    messages.success(request, f'スレッド「{thread.title}」を削除しました')
    return redirect('codemon:thread_list')


@require_POST
def score_thread(request, thread_id):
    """教師がスレッド単位で点数を付ける。POST: {'score': int, 'comment': str} """
    owner = _get_write_owner(request)
    if owner is None:
        return HttpResponseForbidden('ログインが必要です')

    # Simple role check: Account.type == 'teacher'
    if getattr(owner, 'type', '') != 'teacher':
        return HttpResponseForbidden('教師権限が必要です')

    thread = get_object_or_404(ChatThread, thread_id=thread_id)
    try:
        score_val = int(request.POST.get('score'))
    except Exception:
        return JsonResponse({'error': 'score must be integer'}, status=400)
    comment = request.POST.get('comment', '')

    cs = ChatScore.objects.create(thread=thread, scorer=owner, score=score_val, comment=comment)

    # WebSocket経由で点数付与を通知
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        group_name = f'chat_{thread_id}'
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'chat.score',
                'score': {
                    'id': cs.id,
                    'thread_id': thread.thread_id,
                    'score': score_val,
                    'comment': comment,
                    'scorer_id': owner.user_id,
                    'scorer_name': owner.user_name,
                    'created_at': cs.created_at.isoformat(),
                }
            }
        )
    except Exception:
        # WebSocket通知に失敗しても処理は続行
        pass

    return JsonResponse({'status': 'ok', 'score_id': cs.id})


@require_POST
def score_message(request, message_id):
    """教師が個別メッセージに点数を付与。POST: {'score': int, 'comment': str}"""
    owner = _get_write_owner(request)
    if owner is None:
        return HttpResponseForbidden('ログインが必要です')

    if getattr(owner, 'type', '') != 'teacher':
        return HttpResponseForbidden('教師権限が必要です')

    message = get_object_or_404(ChatMessage, message_id=message_id)
    try:
        score_val = int(request.POST.get('score'))
    except Exception:
        return JsonResponse({'error': 'score must be integer'}, status=400)
    comment = request.POST.get('comment', '')

    # 既存のスコアを更新または新規作成
    cs, created = ChatScore.objects.update_or_create(
        message=message,
        scorer=owner,
        defaults={'score': score_val, 'comment': comment}
    )

    # WebSocket経由で点数付与を通知
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        group_name = f'chat_{message.thread.thread_id}'
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'chat.score',
                'score': {
                    'id': cs.id,
                    'message_id': message.message_id,
                    'thread_id': message.thread.thread_id,
                    'score': score_val,
                    'comment': comment,
                    'scorer_id': owner.user_id,
                    'scorer_name': owner.user_name,
                    'created_at': cs.created_at.isoformat(),
                }
            }
        )
    except Exception:
        # WebSocket通知に失敗しても処理は続行
        pass

    return JsonResponse({'status': 'ok', 'score_id': cs.id})


@require_POST
def delete_message(request, message_id):
    """メッセージ削除（送信者または教師が実行可能）。論理削除フラグを立ててWebSocketで通知する。"""
    owner = _get_write_owner(request)
    if owner is None:
        return HttpResponseForbidden('ログインが必要です')

    message = get_object_or_404(ChatMessage, message_id=message_id)

    # 権限チェック: 発信者本人または教師
    if message.sender != owner and getattr(owner, 'type', '') != 'teacher':
        return HttpResponseForbidden('メッセージの削除には送信者または教師権限が必要です')

    # 論理削除
    message.is_deleted = True
    # 希望があれば本文を置き換える（情報漏洩防止）
    message.content = 'このメッセージは削除されました。'
    message.save()

    # WebSocket経由で削除を通知
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{message.thread.thread_id}',
            {
                'type': 'chat.delete',
                'message_id': message.message_id,
                'deleted_by_id': owner.user_id,
                'deleted_by_name': getattr(owner, 'user_name', ''),
                'deleted_at': timezone.now().isoformat(),
            }
        )
    except Exception:
        pass

    return JsonResponse({'status': 'ok', 'message_id': message.message_id})


@teacher_required
def get_thread_readers(request, thread_id):
    """スレッド内のメッセージ既読者一覧を取得（教師のみ）"""
    owner = _get_write_owner(request)
    thread = get_object_or_404(ChatThread, thread_id=thread_id)

    # スレッドへのアクセス権限をチェック
    if not can_access_thread(owner, thread):
        return HttpResponseForbidden('このスレッドにアクセスする権限がありません')

    # 既読情報を集計
    from .models import ReadReceipt
    readers = ReadReceipt.objects.filter(
        message__thread=thread
    ).values(
        'reader__user_id',
        'reader__user_name',
        'message__message_id',
        'read_at'
    ).distinct().order_by('read_at')

    # 既読者ごとに集計
    reader_summary = {}
    for r in readers:
        reader_id = r['reader__user_id']
        if reader_id not in reader_summary:
            reader_summary[reader_id] = {
                'user_id': reader_id,
                'user_name': r['reader__user_name'],
                'message_count': 0,
                'last_read_at': r['read_at'].isoformat()
            }
        reader_summary[reader_id]['message_count'] += 1

    return JsonResponse({
        'readers': list(reader_summary.values()),
        'total_messages': thread.messages.count()
    })

def checklist_selection(request):
    if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
        # 匿名ユーザーでも動作させる
        checklists = Checklist.objects.all()
    else:
        owner = _get_write_owner(request)
        if owner is None:
            login_url = reverse('accounts:student_login') + '?next=' + request.path
            messages.error(request, 'チェックリストの閲覧にはログインが必要です')
            return redirect(login_url)

        # ログイン済みユーザー向けの一覧を設定
        checklists = Checklist.objects.filter(user=owner).order_by('-updated_at')

    # --- AIキャラクター選択の反映 ---
    try:
        # 優先順: セッションの selected_appearance -> アカウントの AiConfig.appearance -> 既存の session.ai_character -> デフォルト
        appearance_map = {
            'dog': 'inu', 'dog.png': 'inu', 'イヌ': 'inu', '犬': 'inu',
            'cat': 'neko', 'cat.png': 'neko', 'ネコ': 'neko', '猫': 'neko',
            'rabbit': 'usagi', 'rabbit.png': 'usagi', 'ウサギ': 'usagi', '兎': 'usagi',
            'panda': 'panda', 'panda.png': 'panda',
            'fox': 'kitsune', 'fox.png': 'kitsune', 'キツネ': 'kitsune',
            'squirrel': 'risu', 'squirrel.png': 'risu', 'リス': 'risu',
            'owl': 'fukurou', 'owl.png': 'fukurou', 'フクロウ': 'fukurou',
            'alpaca': 'arupaka', 'alpaca.png': 'arupaka', 'アルパカ.png': 'arupaka'
        }

        char = None
        # 1) セッションに一時保存された選択肢
        sel = request.session.get('selected_appearance')
        if sel:
            key = sel.lower().replace('.png', '')
            char = appearance_map.get(key) or appearance_map.get(sel)

        # 2) アカウントに保存された AiConfig
        if not char:
            try:
                from accounts.models import AiConfig
                owner_id = None
                if not getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
                    owner_id = getattr(owner, 'user_id', getattr(owner, 'id', None))
                if owner_id:
                    cfg = AiConfig.objects.filter(user_id=owner_id).first()
                    if cfg and cfg.appearance:
                        key = cfg.appearance.lower().replace('.png', '')
                        char = appearance_map.get(key) or appearance_map.get(cfg.appearance)
            except Exception:
                # ignore and fallback
                pass

        # 3) 既にセッションに入っている値、またはデフォルト
        if not char:
            char = request.session.get('ai_character', 'inu')

        request.session['ai_character'] = char
        request.session.modified = True
    except Exception:
        # 安全性: 例外は握り潰してテンプレートは通常通り描画
        pass

    return render(request, 'codemon/checklist_selection.html', {'checklists': checklists})

def checklist_list(request):
    """作成済みチェックリストの一覧を表示"""
    # user_idパラメータがある場合は、そのユーザーのチェックリストを表示
    target_user_id = request.GET.get('user_id')
    
    if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
        if target_user_id:
            # 特定ユーザーのチェックリストを表示
            try:
                target_user = Account.objects.get(user_id=target_user_id)
                checklists = Checklist.objects.filter(user=target_user).order_by('-updated_at')
            except Account.DoesNotExist:
                checklists = Checklist.objects.none()
        else:
            checklists = Checklist.objects.all().order_by('-updated_at')
    else:
        owner = _get_write_owner(request)
        if owner is None:
            login_url = reverse('accounts:student_login') + '?next=' + request.path
            messages.error(request, 'チェックリストの閲覧にはログインが必要です')
            return redirect(login_url)
        
        if target_user_id:
            # 教員が生徒のチェックリストを閲覧する場合
            try:
                target_user = Account.objects.get(user_id=target_user_id)
                checklists = Checklist.objects.filter(user=target_user).order_by('-updated_at')
            except Account.DoesNotExist:
                checklists = Checklist.objects.none()
        else:
            # 自分のチェックリストを表示
            checklists = Checklist.objects.filter(user=owner).order_by('-updated_at')
    
    return render(request, 'codemon/checklist_list.html', {'checklists': checklists})

def checklist_create(request):
    if request.method == 'POST':
        owner = _get_write_owner(request)
        # Debug logging to help diagnose redirect-to-login issues
        try:
            print(f"DEBUG checklist_create: settings.DEBUG={getattr(settings, 'DEBUG', None)}")
            print(f"DEBUG checklist_create: session_keys={list(request.session.keys())}")
            print(f"DEBUG checklist_create: is_account_authenticated={request.session.get('is_account_authenticated')}")
            print(f"DEBUG checklist_create: request.user.is_authenticated={getattr(request.user, 'is_authenticated', None)}")
            print(f"DEBUG checklist_create: owner before handling = {repr(owner)}")
        except Exception:
            pass
        # If no owner (not logged in), allow creation in DEBUG by creating/using a dev account.
        if owner is None:
            from django.urls import reverse
            # In production, keep the redirect to login for security.
            if not getattr(settings, 'DEBUG', False):
                login_url = reverse('accounts:student_login') + '?next=' + request.path
                messages.error(request, 'チェックリストの作成はログインが必要です。ログインしてください。')
                return redirect(login_url)
            # DEBUG mode: create or get a dev anonymous Account so creation can proceed
            from accounts.models import Account as _Account
            owner, _ = _Account.objects.get_or_create(
                email='dev_auto@local',
                defaults={
                    'user_name': '開発用匿名',
                    'password': 'dev',
                    'account_type': 'dev',
                    'age': 0,
                }
            )
            # Bind the dev account to the current session so subsequent GETs
            # (e.g. redirect to checklist_detail) recognize the owner.
            try:
                request.session['is_account_authenticated'] = True
                # Use owner.user_id if available, otherwise owner.id
                request.session['account_user_id'] = getattr(owner, 'user_id', getattr(owner, 'id', None))
            except Exception:
                pass

        name = request.POST.get('name')
        description = request.POST.get('description', '')
        if name:
            cl = Checklist.objects.create(user=owner, checklist_name=name, checklist_description=description)

            # チェックリスト項目の保存
            sort_order = 1
            for key, value in request.POST.items():
                if key.startswith('item_text_') and value.strip():
                    ChecklistItem.objects.create(
                        checklist=cl,
                        item_text=value.strip(),
                        sort_order=sort_order
                    )
                    sort_order += 1

            messages.success(request, 'チェックリストを作成しました。')
            return redirect('codemon:checklist_detail', pk=cl.checklist_id)
    return render(request, 'codemon/checklist_create.html', {'user': request.user})


def checklist_detail(request, pk):
	if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
		cl = get_object_or_404(Checklist, checklist_id=pk)
	else:
		owner = _get_write_owner(request)
		if owner is None:
			login_url = reverse('accounts:student_login') + '?next=' + request.path
			messages.error(request, 'チェックリストの閲覧にはログインが必要です')
			return redirect(login_url)
		cl = get_object_or_404(Checklist, checklist_id=pk, user=owner)
	if request.method == 'POST':
		# new item
		text = request.POST.get('item_text')
		if text:
			max_order = cl.items.aggregate(models.Max('sort_order'))['sort_order__max'] or 0
			ChecklistItem.objects.create(checklist=cl, item_text=text, sort_order=max_order + 1)
			return redirect('codemon:checklist_detail', pk=pk)
	return render(request, 'codemon/checklist_detail.html', {'checklist': cl})


@require_POST
def checklist_toggle_item(request, pk, item_id):
	if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
		cl = get_object_or_404(Checklist, checklist_id=pk)
	else:
		owner = _get_write_owner(request)
		if owner is None:
			login_url = reverse('accounts:student_login') + '?next=' + request.path
			messages.error(request, 'チェックリストの操作にはログインが必要です')
			return redirect(login_url)
		cl = get_object_or_404(Checklist, checklist_id=pk, user=owner)
	item = get_object_or_404(ChecklistItem, checklist=cl, checklist_item_id=item_id)
	item.is_done = not item.is_done
	item.save()
	return redirect('codemon:checklist_detail', pk=pk)


def checklist_edit(request, pk):
	if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
		cl = get_object_or_404(Checklist, checklist_id=pk)
	else:
		owner = _get_write_owner(request)
		if owner is None:
			login_url = reverse('accounts:student_login') + '?next=' + request.path
			messages.error(request, 'チェックリストの編集にはログインが必要です')
			return redirect(login_url)
		cl = get_object_or_404(Checklist, checklist_id=pk, user=owner)
	return render(request, 'codemon/checklist_edit.html', {'checklist': cl})

def checklist_save(request, pk):
    checklist = get_object_or_404(Checklist, checklist_id=pk)
    if request.method == 'POST':
        name = request.POST.get('checklist_name')
        desc = request.POST.get('checklist_description')

        items = []
        index = 1
        while f'item_{index}' in request.POST:
            text = request.POST.get(f'item_{index}', '').strip()
            done = request.POST.get(f'done_{index}') == 'on'
            if text:
                items.append({'text': text, 'done': done})
            index += 1

        # 🔹 確認画面表示
        if 'show_confirm' in request.POST:
            return render(request, 'codemon/checklist_save.html', {
                'checklist': checklist,
                'checklist_name': name,
                'checklist_description': desc,
                'items': items,
            })

        # 🔹 確定保存
        checklist.checklist_name = name
        checklist.checklist_description = desc
        checklist.updated_at = timezone.now()
        checklist.save()

        checklist.items.all().delete()
        for i, item in enumerate(items, start=1):
            ChecklistItem.objects.create(
                checklist=checklist,
                item_text=item['text'],
                is_done=item['done'],
                sort_order=i
            )

        messages.success(request, 'チェックリストを保存しました。')
        return redirect('codemon:checklist_detail', pk=checklist.checklist_id)

    return redirect('codemon:checklist_edit', pk=pk)

def checklist_delete_confirm(request, pk):
	if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
		cl = get_object_or_404(Checklist, checklist_id=pk)
	else:
		owner = _get_write_owner(request)
		if owner is None:
			login_url = reverse('accounts:student_login') + '?next=' + request.path
			messages.error(request, 'チェックリストの削除にはログインが必要です')
			return redirect(login_url)
		cl = get_object_or_404(Checklist, checklist_id=pk, user=owner)
	return render(request, 'codemon/checklist_delete_confirm.html', {'checklist': cl})


def checklist_delete(request, pk):
    if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
        cl = get_object_or_404(Checklist, checklist_id=pk)
    else:
        owner = _get_write_owner(request)
        if owner is None:
            # In production, require login. In DEBUG allow a dev account and bind session.
            if not getattr(settings, 'DEBUG', False):
                login_url = reverse('accounts:student_login') + '?next=' + request.path
                messages.error(request, 'チェックリストの削除にはログインが必要です')
                return redirect(login_url)
            # DEBUG: create/get dev account and bind to session
            from accounts.models import Account as _Account
            owner, _ = _Account.objects.get_or_create(
                email='dev_auto@local',
                defaults={'user_name': '開発用匿名', 'password': 'dev', 'account_type': 'dev', 'age': 0}
            )
            try:
                request.session['is_account_authenticated'] = True
                request.session['account_user_id'] = getattr(owner, 'user_id', getattr(owner, 'id', None))
            except Exception:
                pass
        cl = get_object_or_404(Checklist, checklist_id=pk, user=owner)
    if request.method == 'POST':
        checklist_name = cl.checklist_name
        items_count = cl.items.count()
        cl.delete()
        messages.success(request,
            f'チェックリスト「{checklist_name}」と{items_count}個の項目が削除されました。')
        return render(request, 'codemon/checklist_delete_complete.html',
            {'deleted_name': checklist_name, 'deleted_items_count': items_count})
    return redirect('codemon:checklist_delete_confirm', pk=pk)


@require_POST
def upload_attachments(request):
    """Handle file upload for chat. Creates a ChatMessage (if needed) and a ChatAttachment,
    then broadcasts the message to the thread group so WebSocket clients receive it.

    Expected POST fields:
    - thread_id: int
    - sender_id: int (optional if ALLOW_ANONYMOUS_VIEWS)
    - file: uploaded file
    """
    owner = _get_write_owner(request)
    if owner is None:
        return HttpResponseForbidden('ログインが必要です')

    thread_id = request.POST.get('thread_id')
    if not thread_id:
        return JsonResponse({'error': 'thread_id is required'}, status=400)

    try:
        thread = ChatThread.objects.get(thread_id=thread_id)
    except ChatThread.DoesNotExist:
        # create a simple thread if not exists
        thread = ChatThread.objects.create(thread_id=thread_id, title=f'Thread {thread_id}', created_by=owner)

    # Support multiple files uploaded under the key 'files' (FormData.append('files', file))
    upload_files = request.FILES.getlist('files') or []
    # Fallback to single-file key 'file' for backward compatibility
    single = request.FILES.get('file')
    if single and not upload_files:
        upload_files = [single]

    if not upload_files:
        return JsonResponse({'error': 'file is required'}, status=400)

    # Validate each file and create attachments
    attachments_created = []
    # Create a single ChatMessage for all uploaded files
    msg = ChatMessage.objects.create(thread=thread, sender=owner, content='')

    for upload_file in upload_files:
        # ファイルサイズの検証
        if upload_file.size > settings.MAX_UPLOAD_SIZE:
            max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
            return JsonResponse({
                'error': f'ファイルサイズは{max_mb}MB以下にしてください'
            }, status=400)

        # 拡張子の検証
        ext = os.path.splitext(upload_file.name)[1].lower()
        if ext not in settings.ALLOWED_UPLOAD_EXTENSIONS:
            allowed = ', '.join(settings.ALLOWED_UPLOAD_EXTENSIONS)
            return JsonResponse({
                'error': f'許可されているファイル形式: {allowed}'
            }, status=400)

        chat_attachment = ChatAttachment.objects.create(message=msg, file=upload_file)
        attachments_created.append(chat_attachment)

    # Prepare payload to broadcast (match consumer payload shape)
    attachments_payload = []
    import mimetypes as _mimetypes
    for a, original in zip(attachments_created, upload_files):
        attachments_payload.append({
            'attachment_id': a.attachment_id,
            'url': a.file.url,
            'filename': getattr(original, 'name', ''),
            'mime_type': _mimetypes.guess_type(getattr(a.file, 'name', ''))[0]
        })

    message_payload = {
        'message_id': msg.message_id,
        'thread_id': thread.thread_id,
        'sender_id': owner.user_id,
        'sender_name': getattr(owner, 'user_name', ''),
        'content': msg.content,
        'created_at': msg.created_at.isoformat(),
        'attachments': attachments_payload
    }

    # Broadcast to channel layer
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        group_name = f'chat_{thread.thread_id}'
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'chat.message',
                'message': message_payload,
            }
        )
    except Exception:
        # If channel layer fails, ignore and just return success
        pass

    return JsonResponse({'status': 'ok', 'message': message_payload})


@login_required
def download_attachment(request, attachment_id):
    """
    添付ファイルをダウンロードする安全なエンドポイント
    - ユーザー認証必須
    - Content-Dispositionでファイル名を制御
    - Content-Typeで適切なMIMEタイプを設定
    - スレッドの閲覧権限をチェック
    """
    owner = _get_write_owner(request)
    if owner is None:
        return HttpResponseForbidden('ログインが必要です')

    # 添付ファイルと関連メッセージを取得
    attachment = get_object_or_404(ChatAttachment, attachment_id=attachment_id)
    message = attachment.message
    thread = message.thread

    # メッセージの削除チェック
    if message.is_deleted:
        return HttpResponseForbidden('このメッセージは削除されています')

    # スレッドのアクセス制御
    if not thread.is_active:
        return HttpResponseForbidden('このスレッドは無効化されています')

    if thread.group:
        # グループに所属している必要がある
        if not GroupMember.objects.filter(group=thread.group, member=owner).exists():
            return HttpResponseForbidden('このファイルにアクセスする権限がありません')
    elif owner.type != 'teacher' and thread.created_by != owner:
        # グループなしの場合、教師か作成者のみアクセス可能
        return HttpResponseForbidden('このファイルにアクセスする権限がありません')
    # if not thread.can_access(owner):
    #     return HttpResponseForbidden('このスレッドにアクセスする権限がありません')

    # ファイルの存在チェック
    if not attachment.file:
        return JsonResponse({'error': '添付ファイルが見つかりません'}, status=404)

    # ファイル名の取得と文字エンコーディング対応
    filename = os.path.basename(attachment.file.name)
    try:
        # RFC 5987 エンコーディング
        from urllib.parse import quote
        filename_header = quote(filename.encode('utf-8'))
        content_disp = f'attachment; filename*=UTF-8\'\'{filename_header}'
    except Exception:
        content_disp = f'attachment; filename="{filename}"'

    # Content-Typeの設定
    import mimetypes
    content_type, _ = mimetypes.guess_type(filename)
    if not content_type:
        content_type = 'application/octet-stream'

    # レスポンスの生成
    from django.http import FileResponse
    response = FileResponse(attachment.file.open('rb'), content_type=content_type)
    response['Content-Disposition'] = content_disp
    
    # キャッシュ制御（任意）
    response['Cache-Control'] = 'private, no-cache'
    
    return response

# グループ管理ビュー
def group_list(request):
    """グループ一覧を表示。教師は作成したグループ、学生は参加しているグループを表示。"""
    owner = _get_write_owner(request)
    if owner is None:
        from django.urls import reverse
        login_url = reverse('accounts:student_login') + '?next=' + request.path
        messages.error(request, 'グループ機能の利用にはログインが必要です')
        return redirect(login_url)

    # 教師の場合は作成したグループ、学生の場合は参加しているグループを表示
    if owner.type == 'teacher':
        groups = Group.objects.filter(owner=owner, is_active=True)
    else:
        # 一部の環境で reverse relation に対する lookup が許可されない場合があるため
        # 明示的に GroupMember を参照して参加中のグループを取得する方式に変更する。
        # DBのスキーマによっては group_member.is_active カラムが存在しないことがあるため
        # まずは is_active を参照せずに参加中の group_id を取得する（後段で Group.is_active を確認する）
        member_group_ids = GroupMember.objects.filter(member=owner).values_list('group_id', flat=True)
        groups = Group.objects.filter(group_id__in=member_group_ids, is_active=True)

    return render(request, 'codemon/group_list.html', {
        'groups': groups,
        'is_teacher': owner.type == 'teacher'
    })


def group_detail(request, group_id):
    """グループ詳細。メンバー一覧、スレッド一覧を表示。"""
    owner = _get_write_owner(request)
    if owner is None:
        messages.error(request, 'ログインが必要です')
        return redirect('accounts:student_login')

    # グループと権限のチェック
    group = get_object_or_404(Group, group_id=group_id, is_active=True)
    try:
        membership = GroupMember.objects.get(
            group=group,
            member=owner,
            is_active=True
        )
    except GroupMember.DoesNotExist:
        return HttpResponseForbidden('このグループにアクセスする権限がありません')

    # グループメンバー一覧を取得
    members = GroupMember.objects.filter(
        group=group,
        is_active=True
    ).select_related('member')

    # グループに関連するスレッドを取得
    threads = ChatThread.objects.filter(group=group, is_active=True).order_by('-created_at')

    return render(request, 'codemon/group_detail.html', {
        'group': group,
        'membership': membership,
        'members': members,
        'threads': threads,
        'is_teacher': owner.type == 'teacher'
    })


def group_create(request):
    """グループ新規作成（教師のみ）"""
    owner = _get_write_owner(request)
    if owner is None or owner.type != 'teacher':
        messages.error(request, 'グループの作成には教師権限が必要です')
        return redirect('codemon:group_list')

    if request.method == 'POST':
        name = request.POST.get('group_name', '').strip()
        description = request.POST.get('description', '').strip()

        if not name:
            messages.error(request, 'グループ名は必須です')
        else:
            # Some legacy DB schemas include a non-null `password` column
            # on the `group` table that is not represented in the Django
            # model. To avoid IntegrityError on insert, perform a raw
            # INSERT specifying a safe empty password value and return
            # the created primary key, then fetch the ORM object.
            try:
                from django.db import connection
                now = timezone.now()
                with connection.cursor() as cursor:
                    cursor.execute(
                        'INSERT INTO "group" (group_name, description, user_id, password, created_at, updated_at, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING group_id',
                        [name, description, getattr(owner, 'user_id', getattr(owner, 'id', None)), '', now, now, True]
                    )
                    row = cursor.fetchone()
                    group_id = row[0]
                group = Group.objects.get(group_id=group_id)
            except Exception:
                # Fall back to the ORM create to let the original exception
                # propagate if raw SQL fails for some reason.
                group = Group.objects.create(
                    group_name=name,
                    description=description,
                    owner=owner
                )
            # 作成者を教師権限のメンバーとして追加
            try:
                GroupMember.objects.create(
                    group=group,
                    member=owner,
                    role='teacher'
                )
            except Exception:
                # Some environments have different legacy column names or
                # additional NOT NULL columns on `group_member`. Try several
                # raw INSERT patterns (common variants) until one succeeds.
                from django.db import connection
                now = timezone.now()
                member_val = getattr(owner, 'user_id', getattr(owner, 'id', None))
                if not member_val:
                    raise ValueError('owner has no id; cannot insert group member')

                last_exc = None
                inserted = False
                variants = [
                    # common: member_user_id column (the model's mapping)
                    ('INSERT INTO "group_member" (group_id, member_user_id, role, created_at) VALUES (%s, %s, %s, %s)', [group.group_id, member_val, 'teacher', now]),
                    # some older schemas: member_id column
                    ('INSERT INTO "group_member" (group_id, member_id, role, created_at) VALUES (%s, %s, %s, %s)', [group.group_id, member_val, 'teacher', now]),
                    # try inserting both columns where both exist and one of them is required
                    ('INSERT INTO "group_member" (group_id, member_user_id, member_id, role, created_at) VALUES (%s, %s, %s, %s, %s)', [group.group_id, member_val, member_val, 'teacher', now]),
                    # variants including is_active column if present
                    ('INSERT INTO "group_member" (group_id, member_user_id, role, created_at, is_active) VALUES (%s, %s, %s, %s, %s)', [group.group_id, member_val, 'teacher', now, True]),
                    ('INSERT INTO "group_member" (group_id, member_id, role, created_at, is_active) VALUES (%s, %s, %s, %s, %s)', [group.group_id, member_val, 'teacher', now, True]),
                ]

                with connection.cursor() as cursor:
                    for sql, params in variants:
                        try:
                            cursor.execute(sql, params)
                            inserted = True
                            break
                        except Exception as e:
                            last_exc = e
                            # try next variant
                            continue

                if not inserted:
                    # Nothing worked — surface the last DB exception so the
                    # developer can inspect the exact schema mismatch.
                    raise last_exc
            messages.success(request, f'グループ「{name}」を作成しました')
            # Immediately render the group detail page so the user stays on the
            # result of the creation without an extra redirect. This mirrors
            # the logic in `group_detail` to assemble members and threads.
            try:
                membership = GroupMember.objects.get(group=group, member=owner, is_active=True)
            except Exception:
                # Fallback for legacy schemas without is_active
                membership = GroupMember.objects.filter(group=group, member=owner).first()

            members_qs = GroupMember.objects.filter(group=group).select_related('member')
            threads = ChatThread.objects.filter(group=group, is_active=True).order_by('-created_at')

            return render(request, 'codemon/group_detail.html', {
                'group': group,
                'membership': membership,
                'members': members_qs,
                'threads': threads,
                'is_teacher': True,
            })

    return render(request, 'codemon/group_create.html')

@require_POST
def group_remove_member(request, group_id, member_id):
    """グループからメンバーを削除（教師のみ）"""
    owner = _get_write_owner(request)
    if owner is None or owner.type != 'teacher':
        return HttpResponseForbidden('教師権限が必要です')

    group = get_object_or_404(Group, group_id=group_id, is_active=True)
    if group.owner != owner:
        return HttpResponseForbidden('グループのオーナーのみメンバーを削除できます')

    try:
        membership = GroupMember.objects.get(
            group=group,
            member_id=member_id,
            is_active=True
        )
        if membership.member == group.owner:
            return JsonResponse({
                'error': 'グループのオーナーは削除できません'
            }, status=400)

        # 論理削除
        membership.is_active = False
        membership.save()

        return JsonResponse({
            'status': 'ok',
            'message': f'{membership.member.user_name}をグループから削除しました'
        })

    except GroupMember.DoesNotExist:
        return JsonResponse({
            'error': '指定されたメンバーが見つかりません'
        }, status=404)


@require_POST
def group_leave(request, group_id):
    """グループから脱退（オーナー以外）"""
    owner = _get_write_owner(request)
    if owner is None:
        return HttpResponseForbidden('ログインが必要です')

    group = get_object_or_404(Group, group_id=group_id, is_active=True)
    if group.owner == owner:
        return HttpResponseForbidden('グループのオーナーは脱退できません')

    try:
        membership = GroupMember.objects.get(group=group, member=owner)
        # 実運用上は is_active カラムが存在しない環境もあるため、削除して対応
        membership.delete()

        messages.success(request, f'グループ「{group.group_name}」から脱退しました')
        return redirect('codemon:group_list')

    except GroupMember.DoesNotExist:
        messages.error(request, 'このグループのメンバーではありません')
        return redirect('codemon:group_list')


def group_edit(request, group_id):
    """グループ情報の編集（教師のみ）"""
    owner = _get_write_owner(request)
    if owner is None or owner.type != 'teacher':
        messages.error(request, '教師権限が必要です')
        return redirect('codemon:group_list')

    group = get_object_or_404(Group, group_id=group_id, owner=owner, is_active=True)

    if request.method == 'POST':
        name = request.POST.get('group_name', '').strip()
        description = request.POST.get('description', '').strip()

        if not name:
            messages.error(request, 'グループ名は必須です')
        else:
            group.group_name = name
            group.description = description
            group.save()
            messages.success(request, f'グループ「{name}」を更新しました')
            return redirect('codemon:group_detail', group_id=group.group_id)

    return render(request, 'codemon/group_edit.html', {'group': group})


@require_POST
def group_delete(request, group_id):
    """グループの削除（論理削除）"""
    owner = _get_write_owner(request)
    if owner is None or owner.type != 'teacher':
        return HttpResponseForbidden('教師権限が必要です')

    group = get_object_or_404(Group, group_id=group_id, owner=owner, is_active=True)
    
    # 実際にグループを削除する（トランザクションでメンバー削除、アカウント紐付け解除、本体削除をまとめて行う）
    try:
        with transaction.atomic():
            # メンバーシップ削除
            GroupMember.objects.filter(group=group).delete()
            # account テーブルの group_id を解除（参照整合性のため）
            try:
                Account.objects.filter(group_id=group.group_id).update(group_id=None)
            except Exception:
                import logging
                logging.exception('failed to clear account.group_id for group %s', group.group_id)
            # グループ本体を削除
            group_name = group.group_name
            group.delete()

        # AJAX 呼び出しなら JSON を返す
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok', 'group_id': group_id, 'message': f'グループ「{group_name}」を削除しました'})

        messages.success(request, f'グループ「{group_name}」を削除しました')
        return redirect('codemon:group_list')
    except Exception as e:
        import logging
        logging.exception('group_delete failed for group_id=%s', group_id)
        messages.error(request, f'グループの削除に失敗しました: {e}')
        return redirect('codemon:group_detail', group_id=group_id)


# If ALLOW_ANONYMOUS_VIEWS is False, wrap the view callables with the real
# login_required decorator so the production behavior is preserved. When the
# flag is True (development), views are left undecorated so anonymous access
# is allowed.
if not getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
    # Wrap only the view callables that are actually present in this module.
    # Some view functions (e.g. group_detail) may be defined elsewhere or omitted
    # in certain branches, so avoid referencing names that don't exist which
    # caused import-time NameError in some environments.
    _to_wrap = [
        'systems_list', 'algorithms_list',
        'checklist_toggle_item',
        'score_thread', 'get_thread_readers',
        # group management related
        'group_list', 'group_create', 'group_detail', 'group_edit',
        'group_invite', 'group_remove_member', 'group_leave'
    ]
    for _name in _to_wrap:
        _fn = globals().get(_name)
        if callable(_fn):
            # Use the module-local `login_required` which may be the
            # custom session-based decorator or a no-op in development
            # when ALLOW_ANONYMOUS_VIEWS=True. Previously this used
            # Django's `_login_required` which forced Django auth redirects.
            globals()[_name] = login_required(_fn)

@login_required
def search_messages(request):
    """
    チャットメッセージを検索するビュー。
    GET パラメータ:
      ?q=検索キーワード
    """
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        results = ChatMessage.objects.filter(
            Q(content__icontains=query),
            is_deleted=False
        ).select_related('sender', 'thread').order_by('-created_at')[:100]

    return render(request, 'codemon/search_results.html', {
        'query': query,
        'results': results
    })
def index(request):
    return render(request, 'codemon/index.html')


# ====== AI Chat API ======
def account_or_login_required(view_func):
    """
    Custom decorator that checks both Django auth and custom session auth
    """
    def wrapper(request, *args, **kwargs):
        # Check Django standard authentication
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        # Check custom session authentication
        if request.session.get('is_account_authenticated'):
            return view_func(request, *args, **kwargs)
        # Not authenticated
        return JsonResponse({"error": "authentication required"}, status=401)
    return wrapper


@account_or_login_required
@require_POST
def ai_chat_api(request):
    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "invalid json"}, status=400)

    message = (body.get("message") or "").strip()
    character = body.get("character") or "usagi"
    conv_id = body.get("conversation_id")

    if not message:
        return JsonResponse({"error": "message required"}, status=400)
    
    # Get Account instance for custom session auth
    from accounts.models import Account
    if request.user.is_authenticated:
        # Djangoユーザーのメールから Account を解決
        account = Account.objects.filter(email=getattr(request.user, 'email', None)).first()
        if not account:
            # セッションに user_id があればフォールバック
            account_user_id = request.session.get('account_user_id')
            if account_user_id:
                account = Account.objects.filter(user_id=account_user_id).first()
        if not account:
            return JsonResponse({"error": "account not found for user"}, status=404)
    else:
        # Custom session authentication
        account_user_id = request.session.get('account_user_id')
        if not account_user_id:
            return JsonResponse({"error": "user identification failed"}, status=401)
        try:
            account = Account.objects.get(user_id=account_user_id)
        except Account.DoesNotExist:
            return JsonResponse({"error": "account not found"}, status=404)

    if conv_id:
        try:
            conv = AIConversation.objects.get(id=conv_id, user=account)
        except AIConversation.DoesNotExist:
            return JsonResponse({"error": "conversation not found"}, status=404)
    else:
        conv = AIConversation.objects.create(
            user=account,
            character_id=character,
            title=f"{character}-{timezone.now():%Y%m%d%H%M}",
        )

    recent = list(conv.messages.order_by("-created_at")[:20])
    pairs = [(m.role, m.content) for m in reversed(recent)]

    AIMessage.objects.create(conversation=conv, role="user", content=message)

    from .services import chat_gemini
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Calling chat_gemini with character={character}, message={message[:50]}...")
        reply = chat_gemini(message, pairs, character_id=character)
        logger.info(f"Got reply: {reply[:100]}...")
    except Exception as e:
        logger.error(f"Error in chat_gemini: {str(e)}", exc_info=True)
        reply = f"[エラー] {str(e)}"

    AIMessage.objects.create(conversation=conv, role="assistant", content=reply)

    return JsonResponse({
        "conversation_id": conv.id,
        "reply": reply,
    })


@account_or_login_required
def ai_history_api(request):
    conv_id = request.GET.get("conversation_id")
    if not conv_id:
        return JsonResponse({"error": "conversation_id required"}, status=400)
    
    # Get Account instance (same logic as ai_chat_api)
    from accounts.models import Account
    if request.user.is_authenticated:
        account = Account.objects.filter(email=getattr(request.user, 'email', None)).first()
        if not account:
            account_user_id = request.session.get('account_user_id')
            if account_user_id:
                account = Account.objects.filter(user_id=account_user_id).first()
        if not account:
            return JsonResponse({"error": "account not found for user"}, status=404)
    else:
        account_user_id = request.session.get('account_user_id')
        if not account_user_id:
            return JsonResponse({"error": "user identification failed"}, status=401)
        try:
            account = Account.objects.get(user_id=account_user_id)
        except Account.DoesNotExist:
            return JsonResponse({"error": "account not found"}, status=404)
    
    try:
        conv = AIConversation.objects.get(id=conv_id, user=account)
    except AIConversation.DoesNotExist:
        return JsonResponse({"error": "not found"}, status=404)

    return JsonResponse({
        "conversation_id": conv.id,
        "character_id": conv.character_id,
        "messages": [
            {"role": m.role, "content": m.content, "created": m.created_at.isoformat()}
            for m in conv.messages.order_by("created_at")
        ],
    })