import json
from functools import wraps
import uuid
import re
import os
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.db import models
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required as _login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseForbidden, FileResponse
# チェックリストアイテム一覧API
from django.views.decorators.http import require_GET

@require_GET
def get_checklist_items_api(request, checklist_id):
    """
    特定のチェックリストに紐づくアイテムをJSON形式で返します
    """
    # checklist_id に紐づくアイテムを取得
    # フィールド名（checklist_id, item_text, is_done）は実際のモデルに合わせて修正してください
    items = ChecklistItem.objects.filter(checklist_id=checklist_id).values(
        'checklist_item_id', 'item_text', 'is_done'
    )
    # 取得したデータをリストにして返す
    return JsonResponse({'items': list(items)})
from django.urls import reverse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .permissions import teacher_required, can_access_thread, can_modify_message
from .models import (
    Checklist, ChecklistItem, ChatThread, ChatScore, ChatMessage, ChatAttachment,
    MessegeGroup, MessegeMember, MessegeGroupInvite,
    DirectMessageThread, DirectMessage,
    AIConversation, AIMessage
)
from accounts.models import Account
from django.utils import timezone
from django.db.models import Q
from django.db import transaction

# 実績システムのビューをインポート
from .views_achievements import achievements_view, claim_achievement_reward, clear_achievement_notifications, claim_all_achievements


# _get_write_owner: セッションまたはrequest.userからAccountを取得
def _get_write_owner(request):
    """セッション認証でユーザーを取得するヘルパー関数"""
    print("=== DEBUG _get_write_owner ===")
    print(f"Session keys: {list(request.session.keys())}")
    print(f"is_account_authenticated: {request.session.get('is_account_authenticated')}")
    print(f"account_user_id: {request.session.get('account_user_id')}")
    
    if not request.session.get('is_account_authenticated'):
        print("Not authenticated - returning None")
        return None
    
    user_id = request.session.get('account_user_id')
    print(f"Got user_id from session: {user_id}")
    
    if not user_id:
        print("No user_id in session - returning None")
        return None
    
    try:
        from accounts.models import Account
        owner = Account.objects.get(user_id=user_id)
        print(f"Found owner: {owner}")
        return owner
    except Account.DoesNotExist:
        print(f"Account not found for user_id={user_id}")
        return None



# 互換用エイリアス（chat側のメッセージグループをGroup名で扱う既存コード向け）
Group = MessegeGroup
GroupMember = MessegeMember

# カスタムログイン必須デコレータ（セッションベース認証用）
def session_login_required(view_func):
	"""
	セッションベースの認証をチェックするデコレータ。
	request.session['is_account_authenticated'] が True でない場合、
	ログインページにリダイレクトします。
	"""
	@wraps(view_func)
	def _wrapped_view(request, *args, **kwargs):
		if not request.session.get('is_account_authenticated'):
			return redirect('accounts:student_login')
		return view_func(request, *args, **kwargs)
		
	return _wrapped_view

if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
    def login_required(fn):
        return fn
else:
    login_required = session_login_required

# 教師専用のログイン必須デコレータ
def teacher_login_required(view_func):
	"""
	教師認証をチェックするデコレータ。
	認証されていない場合、または account_type が teacher でない場合、適切にリダイレクトします。
	"""
	@wraps(view_func)
	def _wrapped_view(request, *args, **kwargs):
		if not request.session.get('is_account_authenticated'):
			return redirect('accounts:teacher_login')
		
		# account_type が teacher であることを確認
		account_type = request.session.get('account_type', '')
		
		# セッションに account_type がない場合は、データベースから取得して更新
		if not account_type:
			user_id = request.session.get('account_user_id')
			if user_id:
				try:
					account = Account.objects.filter(user_id=user_id).first()
					if account:
						account_type = getattr(account, 'account_type', '')
						# セッションを更新
						request.session['account_type'] = account_type
						request.session.modified = True
				except Exception:
					pass
		
		if account_type != 'teacher':
			# 生徒の場合は生徒用チャット画面にリダイレクト
			return redirect('codemon:chat_student')
		return view_func(request, *args, **kwargs)
		
	return _wrapped_view

def account_or_login_required(view_func):
    """
    Custom decorator that checks both Django auth and custom session auth
    """
    def wrapper(request, *args, **kwargs):
        print('DEBUG account_or_login_required: session =', dict(request.session))
        print('DEBUG account_or_login_required: user =', request.user, 'is_authenticated =', getattr(request.user, 'is_authenticated', None))
        # Check Django standard authentication
        if request.user.is_authenticated:
            print('DEBUG account_or_login_required: Django user authenticated')
            return view_func(request, *args, **kwargs)
        # Check custom session authentication
        if request.session.get('is_account_authenticated'):
            print('DEBUG account_or_login_required: session is_account_authenticated = True')
            return view_func(request, *args, **kwargs)
        # Not authenticated
        print('DEBUG account_or_login_required: authentication failed, returning 401')
        return JsonResponse({"error": "authentication required"}, status=401)
    return wrapper

@require_POST
@account_or_login_required
def checklist_toggle_item(request, pk, item_id):
    print('DEBUG checklist_toggle_item: session =', dict(request.session))
    print('DEBUG checklist_toggle_item: user =', request.user, 'is_authenticated =', getattr(request.user, 'is_authenticated', None))
    print('DEBUG checklist_toggle_item: session =', dict(request.session))
    print('DEBUG checklist_toggle_item: user =', getattr(request, 'user', None))
    print('DEBUG checklist_toggle_item: COOKIES =', request.COOKIES)
    print('DEBUG checklist_toggle_item: session =', dict(request.session))
    owner = _get_write_owner(request)
    if owner is None:
        # AjaxリクエストならJsonResponseで401返す
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({'error': 'login required'}, status=401)
        return redirect('accounts:student_login')

    if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
        cl = get_object_or_404(Checklist, checklist_id=pk)
    else:
        cl = get_object_or_404(Checklist, checklist_id=pk, user=owner)

    item = get_object_or_404(ChecklistItem, checklist=cl, checklist_item_id=item_id)

    # Ajax/JSからのリクエストの場合、is_done値を受け取る
    import json
    try:
        data = json.loads(request.body.decode('utf-8'))
        is_done = data.get('is_done', None)
        if isinstance(is_done, bool):
            item.is_done = is_done
            item.save()
            
            # 実績チェック（項目を完了した場合のみ）
            if is_done:
                from codemon.achievement_utils import update_checklist_complete_count
                update_checklist_complete_count(owner)
            
            return JsonResponse({'status': 'ok', 'is_done': item.is_done})
        # is_doneがboolでない場合は反転（従来互換）
    except Exception:
        pass

    # フォールバック: 反転(従来のフォームPOST用)
    item.is_done = not item.is_done
    item.save()
    
    # 実績チェック（項目を完了した場合のみ）
    if item.is_done:
        from codemon.achievement_utils import update_checklist_complete_count
        update_checklist_complete_count(owner)
    
    return redirect('codemon:checklist_detail', pk=pk)
# When ALLOW_ANONYMOUS_VIEWS is True (development convenience), make
# login_required a no-op so pages can be opened without logging in.
if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
	def login_required(fn):
		return fn
else:
	login_required = _login_required


def _get_write_owner(request):
	"""Return an Account instance for writes.
	If user is authenticated, return that Account-like object. If anonymous and
	ALLOW_ANONYMOUS_VIEWS is True, return or create a dev Account.
	Otherwise return None.
	"""
	print("=== DEBUG _get_write_owner (LINE 199) ===")
	print(f"Session keys: {list(request.session.keys())}")
	print(f"is_account_authenticated: {request.session.get('is_account_authenticated')}")
	print(f"account_user_id: {request.session.get('account_user_id')}")
	
	# セッションベース認証をチェック
	if request.session.get('is_account_authenticated'):
		account_user_id = request.session.get('account_user_id')
		print(f"✅ セッション認証OK: account_user_id={account_user_id}")
		if account_user_id:
			try:
				account = Account.objects.get(user_id=account_user_id)
				print(f"✅ Accountを取得: {account}")
				return account
			except Account.DoesNotExist:
				print(f"❌ Account not found for user_id={account_user_id}")
				pass
	else:
		print("❌ is_account_authenticated is False or not set")
	
	# Django標準認証のフォールバック
	if getattr(request, 'user', None) and getattr(request.user, 'is_authenticated', False):
		print(f"🔄 Django標準認証をチェック: email={request.user.email}")
		try:
			account = Account.objects.get(email=request.user.email)
			print(f"✅ Django認証でAccountを取得: {account}")
			return account
		except Account.DoesNotExist:
			print(f"❌ Account not found for email={request.user.email}")
			pass
	
	# 開発用の匿名アカウント
	if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
		print("🔧 開発用匿名アカウントを使用")
		acct, _ = Account.objects.get_or_create(
			email='dev_anonymous@local',
			defaults={'user_name': '開発用匿名', 'password': 'dev', 'account_type': 'dev', 'age': 0}
		)
		return acct
	
	print("❌ 認証失敗 - Noneを返します")
	return None


def _extract_deadline_from_thread(thread):
    """Threadの最初のメッセージから期限日(YYYY-MM-DD)を抽出"""
    try:
        first_message = thread.messages.order_by('created_at').first()
        if not first_message or not first_message.content:
            return None
        match = re.search(r"期限：\s*(\d{4}-\d{2}-\d{2})", first_message.content)
        if not match:
            return None
        return date.fromisoformat(match.group(1))
    except Exception:
        return None


def systems_list(request):
	# placeholder: list systems belonging to user
	systems = []
	return render(request, 'codemon/systems_list.html', {'systems': systems})


def algorithms_list(request):
	algorithms = []
	return render(request, 'codemon/algorithms_list.html', {'algorithms': algorithms})


def chat_view(request):
	# Placeholder chat page; AI integration can be added later
	return render(request, 'codemon/chat.html')


def thread_list(request):
    """投函ボックス(スレッド)一覧。教師は作成したスレッド、学生は所属グループのスレッドを閲覧。"""
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
            if not GroupMember.objects.filter(group=thread.group, member=owner, is_active=True).exists():
                return HttpResponseForbidden('このスレッドにアクセスする権限がありません')

    messages_qs = thread.messages.filter(is_deleted=False).select_related('sender').order_by('created_at')
    return render(request, 'codemon/thread_detail.html', {'thread': thread, 'messages': messages_qs})


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


@require_POST
def edit_message(request, message_id):
    """メッセージ編集（送信者本人のみ実行可能）"""
    owner = _get_write_owner(request)
    if owner is None:
        return HttpResponseForbidden('ログインが必要です')

    message = get_object_or_404(ChatMessage, message_id=message_id)

    # 権限チェック: 発信者本人のみ
    if message.sender != owner:
        return HttpResponseForbidden('メッセージの編集には送信者権限が必要です')

    # リクエストボディから新しい内容を取得
    try:
        import json
        data = json.loads(request.body)
        new_content = data.get('content', '').strip()
        
        if not new_content:
            return JsonResponse({'status': 'error', 'error': 'メッセージ内容が空です'}, status=400)
        
        # メッセージ内容を更新
        message.content = new_content
        message.save()

        # WebSocket経由で編集を通知
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'chat_{message.thread.thread_id}',
                {
                    'type': 'chat.edit',
                    'message_id': message.message_id,
                    'content': new_content,
                    'edited_by_id': owner.user_id,
                    'edited_by_name': getattr(owner, 'user_name', ''),
                    'edited_at': timezone.now().isoformat(),
                }
            )
        except Exception:
            pass

        return JsonResponse({
            'status': 'ok',
            'message_id': message.message_id,
            'content': new_content
        })
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'error': '不正なリクエストです'}, status=400)


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
    owner = _get_write_owner(request)
    if owner is None:
        return redirect('accounts:student_login')
    
    if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
        # 匿名ユーザーでも動作させる
        checklists = Checklist.objects.all()
        owner = None
    else:
        owner = _get_write_owner(request)
        if owner is None:
            login_url = reverse('accounts:student_login') + '?next=' + request.path
            messages.error(request, 'チェックリストの閲覧にはログインが必要です')
            return redirect(login_url)

        # owner（Accountオブジェクト）に紐づくチェックリストを取得
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

    # Account オブジェクトをテンプレートコンテキストに追加
    # チェックリスト数と実績称号の取得
    total_checklists = 0
    achievement_title = 'チェックリスト入門'  # デフォルト称号
    
    if owner:
        try:
            from codemon.models import UserStats, Achievement, UserAchievement
            stats, _ = UserStats.objects.get_or_create(user=owner)
            total_checklists = stats.total_checklists_created
            
            # チェックリスト作成実績から現在の称号を取得（達成済みの最高ティア）
            checklist_achievements = UserAchievement.objects.filter(
                user=owner,
                achievement__category='checklist_create',
                is_achieved=True
            ).select_related('achievement').order_by('-achievement__target_count')
            
            if checklist_achievements.exists():
                achievement_title = checklist_achievements.first().achievement.name
            
        except Exception:
            pass
    
    context = {
        'checklists': checklists,
        'account': owner,  # Account オブジェクトをテンプレートで使用可能に
        'total_checklists': total_checklists,
        'achievement_title': achievement_title,
    }

    return render(request, 'codemon/checklist_selection.html', context)

def checklist_list(request):
    """作成済みチェックリストの一覧を表示"""
    owner = _get_write_owner(request)
    if owner is None:
        return redirect('accounts:student_login')
    
    # URLパラメータから対象ユーザーIDを取得
    target_user_id = request.GET.get('user_id')
    
    if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
        checklists = Checklist.objects.all().order_by('-updated_at')
    else:
        # 対象ユーザーが指定されている場合
        if target_user_id:
            # 教師は他のユーザーのチェックリストを閲覧可能
            if getattr(owner, 'type', '') == 'teacher':
                try:
                    target_account = Account.objects.get(user_id=target_user_id)
                    checklists = Checklist.objects.filter(user=target_account).order_by('-updated_at')
                except Account.DoesNotExist:
                    messages.error(request, '指定されたユーザーが見つかりません')
                    checklists = Checklist.objects.filter(user=owner).order_by('-updated_at')
            else:
                # 生徒は自分のチェックリストのみ閲覧可能
                if str(target_user_id) == str(owner.user_id):
                    checklists = Checklist.objects.filter(user=owner).order_by('-updated_at')
                else:
                    messages.error(request, '他のユーザーのチェックリストは閲覧できません')
                    checklists = Checklist.objects.filter(user=owner).order_by('-updated_at')
        else:
            # 対象ユーザーが指定されていない場合は自分のチェックリストを表示
            checklists = Checklist.objects.filter(user=owner).order_by('-updated_at')
    
    return render(request, 'codemon/checklist_list.html', {'checklists': checklists})

def checklist_create(request):
    # 認証チェックを最初に実行
    owner = _get_write_owner(request)
    if owner is None:
        return redirect('accounts:student_login')

    # セッションから編集データを取得
    editing_id = request.session.get('editing_checklist_id')
    editing_name = request.session.get('editing_checklist_name', '')
    editing_description = request.session.get('editing_checklist_description', '')
    editing_due_date = request.session.get('editing_checklist_due_date', '')
    editing_items = request.session.get('editing_checklist_items', [])

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        due_date_str = request.POST.get('due_date', '')
        
        # 期限日の処理
        due_date = None
        if due_date_str:
            try:
                from datetime import datetime
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        if name:
            # 編集モードの場合は既存のチェックリストを更新
            if editing_id:
                cl = get_object_or_404(Checklist, checklist_id=editing_id, user=owner)
                cl.checklist_name = name
                cl.checklist_description = description
                cl.due_date = due_date
                cl.save()
                
                # 既存の項目を削除
                cl.items.all().delete()
            else:
                # 新規作成
                cl = Checklist.objects.create(
                    user=owner, 
                    checklist_name=name, 
                    checklist_description=description,
                    due_date=due_date
                )

            # チェックリスト項目の保存
            items = request.POST.getlist('items[]')
            sort_order = 1
            for value in items:
                if value.strip():
                    ChecklistItem.objects.create(
                        checklist=cl,
                        item_text=value.strip(),
                        sort_order=sort_order
                    )
                    sort_order += 1

            # セッションをクリア
            request.session.pop('editing_checklist_id', None)
            request.session.pop('editing_checklist_name', None)
            request.session.pop('editing_checklist_description', None)
            request.session.pop('editing_checklist_due_date', None)
            request.session.pop('editing_checklist_items', None)

            # 実績チェック（新規作成の場合のみ）
            if not editing_id:
                from codemon.achievement_utils import update_checklist_create_count
                update_checklist_create_count(owner)

            messages.success(request, 'チェックリストを保存しました。')
            return redirect('codemon:checklist_detail', pk=cl.checklist_id)
    
    # 編集データをテンプレートに渡す
    context = {
        'user': owner,
        'editing_name': editing_name,
        'editing_due_date': editing_due_date,
        'editing_description': editing_description,
        'editing_items_json': json.dumps(editing_items),
        'is_editing': bool(editing_id),
    }
    return render(request, 'codemon/checklist_create.html', context)


def checklist_detail(request, pk):
    """チェックリスト作成後、一覧画面にリダイレクト"""
    return redirect('codemon:checklist_list')


def checklist_edit(request, pk):
    """チェックリスト編集（新規作成画面に遷移してフォームに既存データを入力）"""
    print(f"🔍 checklist_edit called: pk={pk}")
    if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
        cl = get_object_or_404(Checklist, checklist_id=pk)
    else:
        owner = _get_write_owner(request)  # ← ownerを取得
        if owner is None:
            return redirect('accounts:student_login')
        cl = get_object_or_404(Checklist, checklist_id=pk, user=owner)  # ← user=ownerに修正
    
    # セッションにチェックリストデータを保存（is_doneは不要）
    request.session['editing_checklist_id'] = pk
    request.session['editing_checklist_name'] = cl.checklist_name
    request.session['editing_checklist_due_date'] = cl.due_date.strftime('%Y-%m-%d') if cl.due_date else ''
    request.session['editing_checklist_description'] = cl.checklist_description or ''
    request.session['editing_checklist_items'] = [
        {'item_text': item.item_text}  # is_doneを削除
        for item in cl.items.all().order_by('sort_order')
    ]
    
    return redirect('codemon:checklist_create')

def checklist_save(request, pk):
    owner = _get_write_owner(request)
    if owner is None:
        return redirect('accounts:student_login')
    
    if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
        checklist = get_object_or_404(Checklist, checklist_id=pk)
    else:
        checklist = get_object_or_404(Checklist, checklist_id=pk, user=owner)
    
    if request.method == 'POST':
        name = request.POST.get('checklist_name')
        desc = request.POST.get('checklist_description', '')

        items = []
        index = 1
        while f'item_title_{index}' in request.POST:
            text = request.POST.get(f'item_title_{index}', '').strip()
            done = request.POST.get(f'item_check_{index}') == 'on'
            if text:
                items.append({'text': text, 'done': done})
            index += 1

        # 🔹 保存確定（編集画面から保存ボタンを押した場合）
        if 'show_confirm' in request.POST or 'confirm_save' in request.POST:
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
            # show_confirmの場合は保存完了画面を表示
            if 'show_confirm' in request.POST:
                return render(request, 'codemon/checklist_save.html', {
                    'checklist': checklist,
                })
            # confirm_saveの場合は詳細画面にリダイレクト
            return redirect('codemon:checklist_detail', pk=checklist.checklist_id)

    return redirect('codemon:checklist_edit', pk=pk)

def checklist_delete_confirm(request, pk):
    """削除確認画面（GET リクエスト用）"""
    # デバッグ情報を出力
    print("=== DEBUG checklist_delete_confirm ===")
    print(f"Session data: {dict(request.session)}")
    print(f"is_account_authenticated: {request.session.get('is_account_authenticated')}")
    print(f"account_user_id: {request.session.get('account_user_id')}")
    
    if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
        cl = get_object_or_404(Checklist, checklist_id=pk)
    else:
        owner = _get_write_owner(request)
        print(f"owner: {owner}")
        if owner is None:
            print("Owner is None - redirecting to login")
            return redirect('accounts:student_login')
        cl = get_object_or_404(Checklist, checklist_id=pk, user=owner)
    
    print(f"Checklist found: {cl}")
    return render(request, 'codemon/checklist_delete_confirm.html', {'checklist': cl})


def checklist_delete(request, pk):
    """削除処理を実行（POST リクエスト用）"""
    if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
        cl = get_object_or_404(Checklist, checklist_id=pk)
    else:
        owner = _get_write_owner(request)
        if owner is None:
            return redirect('accounts:student_login')
        cl = get_object_or_404(Checklist, checklist_id=pk, user=owner)

    if request.method == 'POST':
        checklist_name = cl.checklist_name
        items_count = cl.items.count()
        cl.delete()
        messages.success(request,
            f'チェックリスト「{checklist_name}」と{items_count}個の項目が削除されました。')
        return render(request, 'codemon/checklist_delete_complete.html',
            {'deleted_name': checklist_name, 'deleted_items_count': items_count})
    
    # GET リクエストの場合は確認画面にリダイレクト
    return redirect('codemon:checklist_delete_confirm', pk=pk)


def checklist_delete_complete(request, pk):
    """削除処理を実行して、完了画面をレンダリング"""
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
    try:
        owner = _get_write_owner(request)
        if owner is None:
            print(f"[ERROR] upload_attachments: ログインが必要です")
            return JsonResponse({'error': 'ログインが必要です'}, status=403)

        thread_id = request.POST.get('thread_id')
        print(f"[DEBUG] upload_attachments: thread_id={thread_id}, user={owner.user_id}")
        
        if not thread_id:
            print(f"[ERROR] upload_attachments: thread_id is required")
            return JsonResponse({'error': 'thread_id is required'}, status=400)

        try:
            thread = ChatThread.objects.get(thread_id=thread_id)
            print(f"[DEBUG] upload_attachments: thread found - {thread.title}")
        except ChatThread.DoesNotExist:
            # create a simple thread if not exists
            print(f"[WARNING] upload_attachments: thread not found, creating new thread")
            thread = ChatThread.objects.create(thread_id=thread_id, title=f'Thread {thread_id}', created_by=owner)

        # Support multiple files uploaded under the key 'files' (FormData.append('files', file))
        upload_files = request.FILES.getlist('files') or []
        # Fallback to single-file key 'file' for backward compatibility
        single = request.FILES.get('file')
        if single and not upload_files:
            upload_files = [single]

        print(f"[DEBUG] upload_attachments: files count={len(upload_files)}")
        
        if not upload_files:
            print(f"[ERROR] upload_attachments: file is required")
            return JsonResponse({'error': 'file is required'}, status=400)

        # Validate each file and create attachments
        attachments_created = []
        # Create a single ChatMessage for all uploaded files
        msg = ChatMessage.objects.create(thread=thread, sender=owner, content='')
        print(f"[DEBUG] upload_attachments: created message {msg.message_id}")

        for upload_file in upload_files:
            print(f"[DEBUG] upload_attachments: processing file {upload_file.name}, size={upload_file.size}")
            
            # ファイルサイズの検証
            if upload_file.size > settings.MAX_UPLOAD_SIZE:
                max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
                error_msg = f'ファイルサイズは{max_mb}MB以下にしてください'
                print(f"[ERROR] upload_attachments: {error_msg}")
                return JsonResponse({'error': error_msg}, status=400)

            # 拡張子の検証
            ext = os.path.splitext(upload_file.name)[1].lower()
            print(f"[DEBUG] upload_attachments: file extension={ext}")
            
            if ext not in settings.ALLOWED_UPLOAD_EXTENSIONS:
                allowed = ', '.join(settings.ALLOWED_UPLOAD_EXTENSIONS)
                error_msg = f'許可されているファイル形式: {allowed}'
                print(f"[ERROR] upload_attachments: {error_msg}")
                return JsonResponse({'error': error_msg}, status=400)

            chat_attachment = ChatAttachment.objects.create(message=msg, file=upload_file)
            attachments_created.append(chat_attachment)
            print(f"[DEBUG] upload_attachments: created attachment {chat_attachment.attachment_id}")

        # Prepare payload to broadcast (match consumer payload shape)
        attachments_payload = []
        import mimetypes as _mimetypes
        for a, original in zip(attachments_created, upload_files):
            attachments_payload.append({
                'id': a.attachment_id,
                'attachment_id': a.attachment_id,
                'url': a.file.url,
                'download_url': reverse('codemon:download_attachment', args=[a.attachment_id]),
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
        except Exception as e:
            # If channel layer fails, ignore and just return success
            print(f"[WARNING] upload_attachments: channel layer broadcast failed - {e}")
            pass

        print(f"[DEBUG] upload_attachments: success - message_id={msg.message_id}, attachments={len(attachments_created)}")
        return JsonResponse({'status': 'ok', 'message': message_payload})
    
    except Exception as e:
        import traceback
        print(f"[ERROR] upload_attachments: unexpected error")
        print(traceback.format_exc())
        return JsonResponse({'error': f'サーバーエラー: {str(e)}'}, status=500)


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
        if not GroupMember.objects.filter(group=thread.group, member=owner, is_active=True).exists():
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
        groups = Group.objects.filter(
            memberships__member=owner,
            memberships__is_active=True,
            is_active=True
        ).distinct()

    return render(request, 'chat/messege_group_management_teacher.html', {
        'groups': groups,
        'is_teacher': owner.type == 'teacher'
    })

def group_invite(request, group_id):
    """グループにメンバーを招待（教師のみ）"""
    owner = _get_write_owner(request)
    if owner is None or owner.type != 'teacher':
        return HttpResponseForbidden('教師権限が必要です')

    group = get_object_or_404(Group, group_id=group_id, is_active=True)
    if group.owner != owner:
        return HttpResponseForbidden('グループのオーナーのみメンバーを招待できます')

    # メールアドレスまたはユーザーIDで招待
    identifier = request.POST.get('identifier', '').strip()
    role = request.POST.get('role', 'student')
    
    if not identifier:
        return JsonResponse({'error': 'メールアドレスまたはユーザーIDを入力してください'}, status=400)

    try:
        # メールアドレスかユーザーIDで検索
        if '@' in identifier:
            member = Account.objects.get(email=identifier)
        else:
            member = Account.objects.get(user_id=identifier)

        # 既存メンバーシップの確認
        membership, created = GroupMember.objects.get_or_create(
            group=group,
            member=member,
            defaults={'role': role, 'is_active': True}
        )

        if not created and not membership.is_active:
            # 非アクティブなメンバーシップを再アクティブ化
            membership.is_active = True
            membership.role = role
            membership.save()
            return JsonResponse({
                'status': 'ok',
                'message': f'{member.user_name}をグループに再招待しました'
            })
        elif not created:
            return JsonResponse({
                'error': f'{member.user_name}は既にグループのメンバーです'
            }, status=400)

        return JsonResponse({
            'status': 'ok',
            'message': f'{member.user_name}をグループに招待しました',
            'member': {
                'id': member.user_id,
                'name': member.user_name,
                'role': role
            }
        })

    except Account.DoesNotExist:
        return JsonResponse({
            'error': '指定されたユーザーが見つかりません'
        }, status=404)
    
def group_invite(request, group_id):
    """グループにメンバーを招待（教師のみ）"""
    owner = _get_write_owner(request)
    if owner is None or owner.type != 'teacher':
        return HttpResponseForbidden('教師権限が必要です')

    group = get_object_or_404(Group, group_id=group_id, is_active=True)
    if group.owner != owner:
        return HttpResponseForbidden('グループのオーナーのみメンバーを招待できます')

    # メールアドレスまたはユーザーIDで招待
    identifier = request.POST.get('identifier', '').strip()
    role = request.POST.get('role', 'student')
    
    if not identifier:
        return JsonResponse({'error': 'メールアドレスまたはユーザーIDを入力してください'}, status=400)

    try:
        # メールアドレスかユーザーIDで検索
        if '@' in identifier:
            member = Account.objects.get(email=identifier)
        else:
            member = Account.objects.get(user_id=identifier)

        # 既存メンバーシップの確認
        membership, created = GroupMember.objects.get_or_create(
            group=group,
            member=member,
            defaults={'role': role, 'is_active': True}
        )

        if not created and not membership.is_active:
            # 非アクティブなメンバーシップを再アクティブ化
            membership.is_active = True
            membership.role = role
            membership.save()
            return JsonResponse({
                'status': 'ok',
                'message': f'{member.user_name}をグループに再招待しました'
            })
        elif not created:
            return JsonResponse({
                'error': f'{member.user_name}は既にグループのメンバーです'
            }, status=400)

        return JsonResponse({
            'status': 'ok',
            'message': f'{member.user_name}をグループに招待しました',
            'member': {
                'id': member.user_id,
                'name': member.user_name,
                'role': role
            }
        })

    except Account.DoesNotExist:
        return JsonResponse({
            'error': '指定されたユーザーが見つかりません'
        }, status=404)


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
            group = Group.objects.create(
                group_name=name,
                description=description,
                owner=owner
            )
            # 作成者を教師権限のメンバーとして追加
            GroupMember.objects.create(
                group=group,
                member=owner,
                role='teacher'
            )
            messages.success(request, f'グループ「{name}」を作成しました')
            return redirect('codemon:group_detail', group_id=group.group_id)

    return render(request, 'codemon/group_create.html')


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

    # グループに関連するスレッドを取得（後で実装）
    threads = []  # ChatThread.objects.filter(group=group).order_by('-created_at')

    return render(request, 'codemon/group_detail.html', {
        'group': group,
        'membership': membership,
        'members': members,
        'threads': threads,
        'is_teacher': owner.type == 'teacher'
    })


@require_POST
def group_invite(request, group_id):
    """グループにメンバーを招待（教師のみ）"""
    owner = _get_write_owner(request)
    if owner is None or owner.type != 'teacher':
        return HttpResponseForbidden('教師権限が必要です')

    group = get_object_or_404(Group, group_id=group_id, is_active=True)
    if group.owner != owner:
        return HttpResponseForbidden('グループのオーナーのみメンバーを招待できます')

    # メールアドレスまたはユーザーIDで招待
    identifier = request.POST.get('identifier', '').strip()
    role = request.POST.get('role', 'student')
    
    if not identifier:
        return JsonResponse({'error': 'メールアドレスまたはユーザーIDを入力してください'}, status=400)

    try:
        # メールアドレスかユーザーIDで検索
        if '@' in identifier:
            member = Account.objects.get(email=identifier)
        else:
            member = Account.objects.get(user_id=identifier)

        # 既存メンバーシップの確認
        membership, created = GroupMember.objects.get_or_create(
            group=group,
            member=member,
            defaults={'role': role, 'is_active': True}
        )

        if not created and not membership.is_active:
            # 非アクティブなメンバーシップを再アクティブ化
            membership.is_active = True
            membership.role = role
            membership.save()
            return JsonResponse({
                'status': 'ok',
                'message': f'{member.user_name}をグループに再招待しました'
            })
        elif not created:
            return JsonResponse({
                'error': f'{member.user_name}は既にグループのメンバーです'
            }, status=400)

        return JsonResponse({
            'status': 'ok',
            'message': f'{member.user_name}をグループに招待しました',
            'member': {
                'id': member.user_id,
                'name': member.user_name,
                'role': role
            }
        })

    except Account.DoesNotExist:
        return JsonResponse({
            'error': '指定されたユーザーが見つかりません'
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
        membership = GroupMember.objects.get(
            group=group,
            member=owner,
            is_active=True
        )
        # 論理削除
        membership.is_active = False
        membership.save()

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
            return redirect('codemon:group_list')

    return render(request, 'chat/messege_group_edit_teacher.html', {'group': group})


def group_member_delete(request, group_id, member_id):
    """グループメンバーの削除確認画面"""
    owner = _get_write_owner(request)
    if owner is None or owner.type != 'teacher':
        messages.error(request, '教師権限が必要です')
        return redirect('codemon:group_list')
    
    group = get_object_or_404(MessegeGroup, group_id=group_id, owner=owner, is_active=True)
    member = get_object_or_404(Account, user_id=member_id)
    
    try:
        membership = MessegeMember.objects.get(group=group, member=member, is_active=True)
    except MessegeMember.DoesNotExist:
        messages.error(request, 'メンバーが見つかりません')
        return redirect('codemon:messege_group_edit', group_id=group_id)
    
    if request.method == 'POST':
        # メンバーを非アクティブ化（削除）
        membership.is_active = False
        membership.save()
        
        messages.success(request, f'{member.user_name}をグループから削除しました')
        return redirect('codemon:group_member_delete_complete', group_id=group_id, member_id=member_id)
    
    context = {
        'group': group,
        'member': member,
        'membership': membership,
    }
    return render(request, 'chat/messege_group_member_delete_teacher.html', context)


def group_member_delete_complete(request, group_id, member_id):
    """グループメンバー削除完了画面"""
    owner = _get_write_owner(request)
    if owner is None or owner.type != 'teacher':
        messages.error(request, '教師権限が必要です')
        return redirect('codemon:group_list')
    
    group = get_object_or_404(MessegeGroup, group_id=group_id, owner=owner, is_active=True)
    member = get_object_or_404(Account, user_id=member_id)
    
    context = {
        'group': group,
        'member': member,
    }
    return render(request, 'chat/messege_group_member_delete_complete_teacher.html', context)


def group_delete(request, group_id):
    """グループの削除（論理削除）"""
    owner = _get_write_owner(request)
    if owner is None or owner.type != 'teacher':
        messages.error(request, '教師権限が必要です')
        return redirect('codemon:group_list')
    
    group = get_object_or_404(Group, group_id=group_id, owner=owner, is_active=True)
    
    if request.method == 'POST':
        # 削除前にグループ情報を保存
        group_name = group.group_name
        member_count = group.memberships.filter(is_active=True).count()
        
        # グループを非アクティブ化（論理削除）
        group.is_active = False
        group.save()

        # メンバーシップも非アクティブ化
        GroupMember.objects.filter(group=group).update(is_active=False)

        # セッションに削除情報を保存
        request.session['group_delete_info'] = {
            'group_name': group_name,
            'member_count': member_count,
            'deleted_at': timezone.now().isoformat()
        }

        # JSONレスポンスで成功を返す（AJAX用）
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        
        # フォーム送信時は完了画面へリダイレクト
        return redirect('codemon:group_delete_complete')
    
    # GETリクエストの場合は確認画面を表示
    return render(request, 'chat/messege_group_delete_teacher.html', {'group': group})


def group_delete_complete(request):
    """グループ削除完了画面"""
    owner = _get_write_owner(request)
    if owner is None or owner.type != 'teacher':
        return redirect('codemon:group_list')
    
    # セッションから削除情報を取得
    delete_info = request.session.pop('group_delete_info', {})
    
    if not delete_info:
        return redirect('codemon:group_list')
    
    return render(request, 'chat/messege_group_delete_complete_teacher.html', {
        'group_name': delete_info.get('group_name', ''),
        'member_count': delete_info.get('member_count', 0),
        'deleted_at': delete_info.get('deleted_at', '')
    })


# If ALLOW_ANONYMOUS_VIEWS is False, wrap the view callables with the real
# login_required decorator so the production behavior is preserved. When the
# flag is True (development), views are left undecorated so anonymous access
# is allowed.
if not getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
    systems_list = _login_required(systems_list)
    algorithms_list = _login_required(algorithms_list)
    chat_view = _login_required(chat_view)
    # checklist_selection, checklist_list, checklist_create, checklist_detail, checklist_save は _get_write_owner で認証チェック済み
    # checklist_toggle_item = _login_required(checklist_toggle_item)  # ← account_or_login_required で認証判定するため不要
    checklist_save = _login_required(checklist_save)
    # checklist_delete_confirm = _login_required(checklist_delete_confirm)
    # checklist_delete = _login_required(checklist_delete)
    score_thread = _login_required(score_thread)
    get_thread_readers = _login_required(get_thread_readers)
    # グループ管理関連のビュー
    # group_list, group_create, group_detail, group_edit, group_delete は _get_write_owner で認証チェック済み
    group_invite = _login_required(group_invite)
    # group_remove_member は @teacher_login_required デコレータを使用しているため、ここではラップしない
    group_leave = _login_required(group_leave)

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



@account_or_login_required
@require_POST
def ai_chat_api(request):
    print(f"[DEBUG AI CHAT] Method: {request.method}")
    print(f"[DEBUG AI CHAT] Content-Type: {request.content_type}")
    
    try:
        # request.bodyを読み取る前にデバッグ
        body_bytes = request.body
        print(f"[DEBUG AI CHAT] Body length: {len(body_bytes)}")
        print(f"[DEBUG AI CHAT] Body raw: {body_bytes[:200]}")
        
        body = json.loads(body_bytes.decode("utf-8"))
        print(f"[DEBUG AI CHAT] Body parsed: {body}")
    except json.JSONDecodeError as e:
        print(f"[ERROR AI CHAT] JSON decode error: {e}")
        print(f"[ERROR AI CHAT] Body was: {body_bytes}")
        return JsonResponse({"error": f"invalid json: {str(e)}"}, status=400)
    except Exception as e:
        print(f"[ERROR AI CHAT] Exception: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": f"parse error: {str(e)}"}, status=400)

    message = (body.get("message") or "").strip()
    character = body.get("character") or "usagi"
    conv_id = body.get("conversation_id")
    
    # デバッグログ
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"=== AI Chat API Called ===")
    logger.info(f"Received body: {body}")
    logger.info(f"Character ID: {character}")
    logger.info(f"Message: {message}")

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
        
        # 実績チェック: AIチャット作成
        from .achievement_utils import update_ai_chat_count
        newly_achieved = update_ai_chat_count(account)
        # JSONレスポンスなのでセッションに保存して次のページで表示
        # (この場合は次回ページロード時にトースト表示される)
        if newly_achieved and hasattr(request, 'session'):
            if 'achievement_notifications' not in request.session:
                request.session['achievement_notifications'] = []
            for achievement in newly_achieved:
                request.session['achievement_notifications'].append({
                    'name': achievement.name,
                    'icon': achievement.icon,
                    'reward': achievement.reward_coins
                })
            request.session.modified = True

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
    from accounts.views import get_logged_account
    acc = get_logged_account(request)
    if not acc:
        return JsonResponse({"error": "not authenticated"}, status=401)
    
    conv_id = request.GET.get("conversation_id")
    if not conv_id:
        return JsonResponse({"error": "conversation_id required"}, status=400)
    try:
        conv = AIConversation.objects.get(id=conv_id, user_id=acc.user_id)
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

# ---- Demo UI views for chat templates ----
def chat_ui_index(request):
    """チャットUIデモ索引ページ"""
    return render(request, 'chat/index.html')

def chat_ui_list(request):
    rooms = [
        {
            'name': '2年A組 グループチャット',
            'is_group': True,
            'avatar_url': None,
            'updated_at': timezone.now(),
            'last_message': '明日の提出物を確認してください。',
            'participant_names': '田中, 鈴木, 佐藤',
            'unread_count': 3,
            'url': reverse('codemon:chat_ui_room'),
        },
        {
            'name': '個別: 山田太郎',
            'is_group': False,
            'avatar_url': None,
            'updated_at': timezone.now() - timezone.timedelta(hours=2),
            'last_message': 'ファイルをアップロードしました。',
            'participant_names': '山田太郎',
            'unread_count': 0,
            'url': reverse('codemon:chat_ui_room'),
        },
    ]
    return render(request, 'chat/chat_list.html', {'chat_rooms': rooms})


def chat_ui_room(request):
    room = {
        'name': '2年A組 グループチャット',
        'is_group': True,
        'member_count': 5,
        'updated_at': timezone.now(),
        'read_ratio': '4/5',
        'unread_count': 1,
        'members': [
            {'name': '田中', 'role': 'teacher'},
            {'name': '佐藤', 'role': 'student'},
            {'name': '鈴木', 'role': 'student'},
            {'name': '山田', 'role': 'student'},
            {'name': '高橋', 'role': 'student'},
        ]
    }

    messages = [
        {
            'author_name': '田中 (教師)',
            'created_at': timezone.now() - timezone.timedelta(minutes=20),
            'text': '課題の提出期限は金曜17:00です。',
            'is_self': False,
            'is_read': True,
            'read_by': '5名',
            'read_count': 5,
            'read_by_list': ['佐藤', '鈴木', '山田', '高橋', '田中'],
            'can_delete': False,
        },
        {
            'author_name': 'あなた',
            'created_at': timezone.now() - timezone.timedelta(minutes=2),
            'text': '了解しました！ファイルも投函します。',
            'is_self': True,
            'is_read': False,
            'read_by': '3名',
            'read_count': 3,
            'read_by_list': ['田中', '佐藤', '山田'],
            'can_delete': True,
            'delete_url': '#',
            'file_url': '/media/sample.pdf',
        },
    ]

    recent_files = [
        {'name': '課題説明.pdf', 'url': '/media/sample.pdf'},
        {'name': '参考画像.png', 'url': '/media/sample.png'},
    ]

    return render(request, 'chat/chat_room.html', {
        'room': room,
        'messages': messages,
        'recent_files': recent_files,
    })


def chat_ui_profile(request):
    return render(request, 'chat/profile_edit.html')


def chat_ui_submission_box(request):
    return render(request, 'chat/submission_box_create.html')


def chat_ui_submission_submit(request):
    assignment = {
        'title': '第3回 レポート',
        'description': 'AIと教育についての考察をまとめてください。',
        'due_at': timezone.now() + timezone.timedelta(days=2),
    }
    submission = {'status': '未提出'}
    return render(request, 'chat/submission_submit.html', {
        'assignment': assignment,
        'submission': submission,
    })


def chat_ui_score_student(request):
    scores = [
        {
            'assignment_title': '第1回 課題',
            'value': 85,
            'max_score': 100,
            'comment': '構成がわかりやすいです',
            'updated_at': timezone.now() - timezone.timedelta(days=1),
        },
        {
            'assignment_title': '第2回 小テスト',
            'value': 92,
            'max_score': 100,
            'comment': '計算ミスに注意',
            'updated_at': timezone.now(),
        },
    ]
    return render(request, 'chat/score_view_student.html', {'scores': scores})


def chat_ui_score_teacher(request):
    score_rows = [
        {'id': 1, 'student_name': '佐藤', 'score': 80, 'max_score': 100, 'comment': 'よくできました'},
        {'id': 2, 'student_name': '鈴木', 'score': 70, 'max_score': 100, 'comment': 'もう一歩'},
    ]
    return render(request, 'chat/score_manage_teacher.html', {'score_rows': score_rows})


def chat_ui_group_manage(request):
    members = [
        {'name': '佐藤', 'role': 'student', 'remove_url': '#'},
        {'name': '鈴木', 'role': 'student', 'remove_url': '#'},
    ]
    return render(request, 'chat/group_manage.html', {'members': members})


# ==================== アクセサリーシステム ====================

@session_login_required
def accessory_shop(request):
    """アクセサリーショップ画面"""
    from .models import Accessory, UserAccessory, UserCoin
    
    user_id = request.session.get('account_user_id')
    user = get_object_or_404(Account, user_id=user_id)
    
    # ユーザーのコイン残高を取得（未作成の場合は作成）
    user_coin, created = UserCoin.objects.get_or_create(user=user)
    
    # 全アクセサリーを取得
    all_accessories = Accessory.objects.all().order_by('category', 'accessory_id')
    
    # ユーザーが所持しているアクセサリーのIDリスト
    owned_accessory_ids = set(
        UserAccessory.objects.filter(user=user).values_list('accessory_id', flat=True)
    )
    
    # 装備中のアクセサリーを取得
    equipped_accessory = UserAccessory.objects.filter(user=user, is_equipped=True).first()
    
    # アクセサリー情報をテンプレート用に整形
    accessories_data = []
    for acc in all_accessories:
        is_owned = acc.accessory_id in owned_accessory_ids
        can_unlock = False
        unlock_reason = ""
        
        if not is_owned:
            if acc.unlock_coins > 0:
                can_unlock = user_coin.balance >= acc.unlock_coins
                unlock_reason = f"{acc.unlock_coins}コイン"
            elif acc.unlock_achievement:
                # 実績による解放（実装は後で拡張可能）
                unlock_reason = f"実績「{acc.unlock_achievement.name}」が必要"
        
        accessories_data.append({
            'accessory': acc,
            'is_owned': is_owned,
            'is_equipped': equipped_accessory and equipped_accessory.accessory_id == acc.accessory_id,
            'can_unlock': can_unlock,
            'unlock_reason': unlock_reason,
        })
    
    context = {
        'user_coin': user_coin,
        'accessories': accessories_data,
        'equipped_accessory': equipped_accessory,
    }
    
    return render(request, 'codemon/accessory_shop.html', context)


@session_login_required
@require_POST
def purchase_accessory(request, accessory_id):
    """アクセサリーを購入"""
    from .models import Accessory, UserAccessory, UserCoin
    
    user_id = request.session.get('account_user_id')
    user = get_object_or_404(Account, user_id=user_id)
    accessory = get_object_or_404(Accessory, accessory_id=accessory_id)
    
    # すでに所持しているかチェック
    if UserAccessory.objects.filter(user=user, accessory=accessory).exists():
        messages.error(request, 'すでに所持しているアクセサリーです。')
        return redirect('codemon:accessory_shop')
    
    # コイン残高チェック
    user_coin, created = UserCoin.objects.get_or_create(user=user)
    
    if user_coin.balance < accessory.unlock_coins:
        messages.error(request, 'コインが足りません。')
        return redirect('codemon:accessory_shop')
    
    # トランザクションで購入処理
    with transaction.atomic():
        # コインを減らす
        user_coin.balance -= accessory.unlock_coins
        user_coin.save()
        
        # アクセサリーを追加
        UserAccessory.objects.create(user=user, accessory=accessory)
        
        # 実績チェック
        from codemon.achievement_utils import update_accessory_purchase_count
        update_accessory_purchase_count(user)
    
    messages.success(request, f'{accessory.name}を購入しました！')
    return redirect('codemon:accessory_shop')


@session_login_required
@require_POST
def equip_accessory(request, accessory_id):
    """アクセサリーを装備"""
    from .models import Accessory, UserAccessory
    
    user_id = request.session.get('account_user_id')
    user = get_object_or_404(Account, user_id=user_id)
    
    # 所持しているかチェック
    user_accessory = get_object_or_404(UserAccessory, user=user, accessory_id=accessory_id)
    
    # トランザクションで装備変更
    with transaction.atomic():
        # 他のアクセサリーの装備を外す（同時装備は1個まで）
        UserAccessory.objects.filter(user=user, is_equipped=True).update(is_equipped=False)
        
        # 指定のアクセサリーを装備
        user_accessory.is_equipped = True
        user_accessory.save()
    
    messages.success(request, f'{user_accessory.accessory.name}を装備しました！')
    return redirect('codemon:accessory_shop')


@session_login_required
@require_POST
def unequip_accessory(request):
    """アクセサリーの装備を外す"""
    from .models import UserAccessory
    
    user_id = request.session.get('account_user_id')
    user = get_object_or_404(Account, user_id=user_id)
    
    # 全ての装備を外す
    UserAccessory.objects.filter(user=user, is_equipped=True).update(is_equipped=False)
    
    messages.success(request, 'アクセサリーを外しました。')
    return redirect('codemon:accessory_shop')

# ========================================
# チャット機能 - 新しいUI画面
# ========================================

def _can_access_group_chat(owner, group):
    if owner is None:
        return False

    # account_type属性を確認（教師の場合はグループのオーナーである必要がある）
    account_type = getattr(owner, 'account_type', '')
    if account_type == 'teacher' and group.owner == owner:
        return True

    # メンバーシップを確認
    return MessegeMember.objects.filter(
        group=group,
        member=owner,
        is_active=True
    ).exists()


def _get_or_create_group_chat_thread(group, owner):
    """グループチャット用のスレッドを取得または作成
    
    投函ボックスとは異なり、グループに対して1つの共有チャットスレッドを使用します。
    title に 'group_chat:' プレフィックスを付けて投函ボックスと区別します。
    """
    title = f'group_chat:{group.group_name}'
    thread = ChatThread.objects.filter(group=group, title=title, is_active=True).first()
    if thread:
        return thread

    created_by = group.owner if group.owner else owner
    return ChatThread.objects.create(
        title=title,
        description='グループチャット用スレッド',
        created_by=created_by,
        group=group
    )


@session_login_required
def group_chat_thread(request, group_id):
    owner = _get_write_owner(request)
    if owner is None:
        return JsonResponse({'error': 'auth_required'}, status=403)

    group = get_object_or_404(MessegeGroup, group_id=group_id, is_active=True)
    if not _can_access_group_chat(owner, group):
        return HttpResponseForbidden('このグループにアクセスする権限がありません')

    thread = _get_or_create_group_chat_thread(group, owner)
    return JsonResponse({'thread_id': thread.thread_id})


@session_login_required
def group_chat_messages(request, group_id):
    print(f"\n[=== group_chat_messages START ===]")
    print(f"[DEBUG] group_id parameter: {group_id}, type: {type(group_id)}")
    
    owner = _get_write_owner(request)
    print(f"[DEBUG] owner after _get_write_owner: {owner}")
    if owner is None:
        print("[ERROR] owner is None, returning 403")
        return JsonResponse({'error': 'auth_required'}, status=403)

    try:
        print(f"[DEBUG] Trying to get MessegeGroup with group_id={group_id}")
        group = get_object_or_404(MessegeGroup, group_id=group_id, is_active=True)
        print(f"[DEBUG] group retrieved: {group}, group_id={group.group_id}, group_name={group.group_name}")
        
        print(f"[DEBUG] Checking access for owner={owner}, group={group}")
        if not _can_access_group_chat(owner, group):
            print("[ERROR] Access denied to group")
            return HttpResponseForbidden('このグループにアクセスする権限がありません')
        
        print(f"[DEBUG] Access granted. Request method: {request.method}")

        if request.method == 'POST':
            # メッセージ送信
            import json
            try:
                data = json.loads(request.body)
                content = data.get('content', '').strip()
                if not content:
                    return JsonResponse({'error': 'メッセージが空です'}, status=400)
                
                thread = _get_or_create_group_chat_thread(group, owner)
                
                # メッセージを作成
                message = ChatMessage.objects.create(
                    thread=thread,
                    sender=owner,
                    content=content
                )
                
                return JsonResponse({
                    'status': 'ok',
                    'message': {
                        'message_id': message.message_id,
                        'sender_user_id': owner.user_id,
                        'sender_name': owner.user_name,
                        'sender_avatar': owner.avatar.url if owner.avatar else None,
                        'content': message.content,
                        'created_at': message.created_at.isoformat(),
                        'read_count': 0,
                        'attachments': []
                    }
                })
            except json.JSONDecodeError:
                return JsonResponse({'error': '不正なリクエスト'}, status=400)
            except Exception as e:
                import traceback
                traceback.print_exc()
                return JsonResponse({'error': str(e)}, status=500)

        # GETリクエスト：メッセージ一覧を取得
        print("[DEBUG] Processing GET request for messages")
        thread = _get_or_create_group_chat_thread(group, owner)
        print(f"[DEBUG] group_chat_messages - thread_id: {thread.thread_id}")
        
        messages_qs = ChatMessage.objects.filter(
            thread=thread,
            is_deleted=False
        ).select_related('sender').prefetch_related('attachments', 'read_receipts').order_by('created_at')
        
        print(f"[DEBUG] group_chat_messages - messages count: {messages_qs.count()}")

        messages = []
        for msg in messages_qs:
            print(f"[DEBUG] Processing message: {msg.message_id}, content: {msg.content[:50] if msg.content else 'None'}")
            
            # 添付ファイルを処理
            attachments_data = []
            for att in msg.attachments.all():
                att_info = {
                    'id': att.attachment_id,
                    'name': att.file.name.split('/')[-1],  # ファイル名のみを取得
                    'url': att.file.url,
                    'download_url': reverse('codemon:download_attachment', args=[att.attachment_id]),
                    'size': att.file.size,  # ファイルサイズを追加
                }
                # 画像ファイルの判定（拡張子で判定）
                image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
                if att.file.name.lower().endswith(image_extensions):
                    att_info['type'] = 'image'
                else:
                    att_info['type'] = 'file'
                attachments_data.append(att_info)
            
            # 既読情報を取得（自分以外の既読者）
            read_by = []
            for receipt in msg.read_receipts.all():
                if receipt.reader.user_id != owner.user_id:
                    read_by.append({
                        'user_id': receipt.reader.user_id,
                        'user_name': receipt.reader.user_name,
                        'read_at': receipt.read_at.isoformat()
                    })
            
            messages.append({
                'message_id': msg.message_id,
                'sender_user_id': msg.sender.user_id,
                'sender_name': getattr(msg.sender, 'user_name', ''),
                'sender_avatar': msg.sender.avatar.url if msg.sender.avatar else None,
                'content': msg.content,
                'created_at': msg.created_at.isoformat(),
                'read_count': len(read_by),  # 自分以外の既読者数
                'read_by': read_by,
                'attachments': attachments_data
            })

        print(f"[DEBUG] Returning {len(messages)} messages")
        print("[=== group_chat_messages END (SUCCESS) ===]\n")
        return JsonResponse({'thread_id': thread.thread_id, 'messages': messages})
    except Exception as e:
        import traceback
        print(f"\n[=== EXCEPTION in group_chat_messages ===]")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        traceback.print_exc()
        print("[=== END ===]\n")
        return JsonResponse({'error': str(e)}, status=500)

@session_login_required
def thread_messages(request, thread_id):
    """投函ボックスのメッセージを取得（投函ボックス詳細画面用）"""
    owner = _get_write_owner(request)
    if owner is None:
        return JsonResponse({'error': 'auth_required'}, status=403)

    thread = get_object_or_404(ChatThread, thread_id=thread_id, is_active=True)
    
    # 権限確認：投函ボックスは'投函ボックス：'で始まる title を持つ
    if not thread.title.startswith('投函ボックス：'):
        return HttpResponseForbidden('このスレッドにアクセスする権限がありません')

    if request.method == 'POST':
        # メッセージ送信
        import json
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()
            if not content:
                return JsonResponse({'error': 'メッセージが空です'}, status=400)
            
            # メッセージを作成
            message = ChatMessage.objects.create(
                thread=thread,
                sender=owner,
                content=content
            )
            
            return JsonResponse({
                'status': 'ok',
                'message': {
                    'message_id': message.message_id,
                    'sender_user_id': owner.user_id,
                    'sender_name': owner.user_name,
                    'sender_avatar': owner.avatar.url if owner.avatar else None,
                    'content': message.content,
                    'created_at': message.created_at.isoformat(),
                    'read_count': 0,
                    'attachments': []
                }
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': '不正なリクエスト'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    # GETリクエスト：メッセージ一覧を取得
    messages_qs = ChatMessage.objects.filter(
        thread=thread,
        is_deleted=False
    ).select_related('sender').prefetch_related('attachments', 'read_receipts').order_by('created_at')

    messages = []
    for msg in messages_qs:
        # 添付ファイルを処理
        attachments_data = []
        for att in msg.attachments.all():
            att_info = {
                'id': att.attachment_id,
                'name': att.file.name.split('/')[-1],  # ファイル名のみを取得
                'url': att.file.url,
                'download_url': reverse('codemon:download_attachment', args=[att.attachment_id]),
                'size': att.file.size,  # ファイルサイズを追加
            }
            # 画像ファイルの判定（拡張子で判定）
            image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
            if att.file.name.lower().endswith(image_extensions):
                att_info['type'] = 'image'
            else:
                att_info['type'] = 'file'
            attachments_data.append(att_info)
        
        messages.append({
            'message_id': msg.message_id,
            'sender_user_id': msg.sender.user_id,
            'sender_name': getattr(msg.sender, 'user_name', ''),
            'sender_avatar': msg.sender.avatar.url if msg.sender.avatar else None,
            'content': msg.content,
            'created_at': msg.created_at.isoformat(),
            'read_count': msg.read_receipts.count(),
            'attachments': attachments_data
        })

    return JsonResponse({'thread_id': thread.thread_id, 'messages': messages})

@session_login_required
def chat_student(request):
    """生徒側チャット画面"""
    user_id = request.session.get('account_user_id')
    
    # 教師の場合は教師用チャット画面にリダイレクト
    account_type = request.session.get('account_type', '')
    if not account_type and user_id:
        # セッションに account_type がない場合は、データベースから取得
        try:
            account = Account.objects.filter(user_id=user_id).first()
            if account:
                account_type = getattr(account, 'account_type', '')
                request.session['account_type'] = account_type
                request.session.modified = True
        except Exception:
            pass
    
    if account_type == 'teacher':
        return redirect('codemon:chat_teacher')
    
    groups = []
    direct_threads = []
    context = {}
    if user_id:
        account = Account.objects.filter(user_id=user_id).first()
        if account:
            print(f"[DEBUG] chat_student - account.avatar: {account.avatar}")
            print(f"[DEBUG] chat_student - has avatar: {bool(account.avatar)}")
            memberships = MessegeMember.objects.filter(member=account, is_active=True).select_related('group')
            groups = [m.group for m in memberships if m.group and m.group.is_active]
            if account.email:
                direct_threads = DirectMessageThread.objects.filter(
                    Q(owner=account) | Q(participant_email=account.email)
                ).order_by('-updated_at')
            # ユーザーのアバター情報をコンテキストに追加
            if account.avatar:
                context['user_avatar'] = account.avatar.url
                print(f"[DEBUG] chat_student - user_avatar: {context['user_avatar']}")
    context['groups'] = groups
    context['direct_threads'] = direct_threads
    print(f"[DEBUG] chat_student - context keys: {context.keys()}")
    return render(request, 'chat/chat_student.html', context)


@teacher_login_required
def chat_teacher(request):
    """教師側チャット画面"""
    user_id = request.session.get('account_user_id')
    groups = []
    direct_threads = []
    context = {}
    selected_group_id = request.GET.get('group')
    
    if user_id:
        account = Account.objects.filter(user_id=user_id).first()
        if account:
            print(f"[DEBUG] chat_teacher - account.avatar: {account.avatar}")
            print(f"[DEBUG] chat_teacher - has avatar: {bool(account.avatar)}")
            owned_groups = MessegeGroup.objects.filter(owner=account, is_active=True)
            memberships = MessegeMember.objects.filter(member=account, is_active=True).select_related('group')
            member_groups = [m.group for m in memberships if m.group and m.group.is_active]
            groups = list(owned_groups) + [g for g in member_groups if g not in owned_groups]
            if account.email:
                direct_threads = DirectMessageThread.objects.filter(
                    Q(owner=account) | Q(participant_email=account.email)
                ).order_by('-updated_at')
            # ユーザーのアバター情報をコンテキストに追加
            if account.avatar:
                context['user_avatar'] = account.avatar.url
                print(f"[DEBUG] chat_teacher - user_avatar: {context['user_avatar']}")
    
    context['groups'] = groups
    context['direct_threads'] = direct_threads
    
    # 選択されたグループの投函ボックスを取得
    # グループチャット用スレッド（title が 'group_chat:' で始まるもの）は除外
    # 投函ボックス用スレッド（title が '投函ボックス：' で始まるもの）のみを取得
    if selected_group_id:
        try:
            selected_group = MessegeGroup.objects.get(group_id=selected_group_id, is_active=True)
            submission_boxes = ChatThread.objects.filter(
                group=selected_group,
                is_active=True,
                title__startswith='投函ボックス：'
            ).order_by('-created_at')
            context['submission_boxes'] = submission_boxes
            context['selected_group_id'] = selected_group_id
        except MessegeGroup.DoesNotExist:
            pass
    
    print(f"[DEBUG] chat_teacher - context keys: {context.keys()}")
    return render(request, 'chat/chat_teacher.html', context)


@session_login_required
def icon_settings_student(request):
    """生徒側アイコン設定"""
    user_id = request.session.get('account_user_id')
    account = Account.objects.filter(user_id=user_id).first() if user_id else None
    context = {}
    if account and account.avatar:
        context['current_avatar'] = account.avatar.url
    return render(request, 'chat/icon_settings_student.html', context)


@teacher_login_required
def icon_settings_teacher(request):
    """教師側アイコン設定"""
    user_id = request.session.get('account_user_id')
    account = Account.objects.filter(user_id=user_id).first() if user_id else None
    context = {}
    if account and account.avatar:
        context['current_avatar'] = account.avatar.url
    return render(request, 'chat/icon_settings_teacher.html', context)


@session_login_required
@require_POST
def save_avatar(request):
    """ユーザーのアバター画像を保存"""
    user_id = request.session.get('account_user_id')
    if not user_id:
        return JsonResponse({'error': 'unauthorized'}, status=403)
    
    try:
        account = Account.objects.get(user_id=user_id)
    except Account.DoesNotExist:
        return JsonResponse({'error': 'user not found'}, status=404)
    
    # ファイルアップロード時
    if 'avatar' in request.FILES:
        avatar_file = request.FILES['avatar']
        account.avatar = avatar_file
        account.save()
        return JsonResponse({
            'status': 'ok',
            'message': 'アバターを保存しました',
            'avatar_url': account.avatar.url
        })
    
    return JsonResponse({'error': 'no file provided'}, status=400)


@session_login_required
def upload_file_student(request):
    """生徒側ファイル投函"""
    return render(request, 'chat/upload_file_student.html')


@teacher_login_required
def upload_file_teacher(request):
    """教師側ファイル投函"""
    return render(request, 'chat/upload_file_teacher.html')


@session_login_required
def upload_image_student(request):
    """生徒側画像投函"""
    return render(request, 'chat/upload_image_student.html')


@teacher_login_required
def upload_image_teacher(request):
    """教師側画像投函"""
    return render(request, 'chat/upload_image_teacher.html')


@teacher_login_required
def chat_invitation(request):
    """教師側メンバー招待"""
    return render(request, 'chat/chat_invitation.html')


@teacher_login_required
@require_POST
def add_group_member(request, group_id):
    """メッセージグループにメンバーを追加（チャット用）"""
    user_id = request.session.get('account_user_id')
    if not user_id:
        messages.error(request, '認証が必要です')
        return redirect('accounts:teacher_login')

    owner = Account.objects.filter(user_id=user_id).first()
    if not owner:
        messages.error(request, 'ユーザーが見つかりません')
        return redirect('accounts:teacher_login')

    group = MessegeGroup.objects.filter(group_id=group_id, owner=owner, is_active=True).first()
    if not group:
        messages.error(request, 'グループが見つかりません')
        return redirect('codemon:chat_teacher')

    identifier = request.POST.get('identifier', '').strip()
    role = request.POST.get('role', 'student')

    if not identifier:
        messages.error(request, 'メールアドレスまたはユーザーIDを入力してください')
        return redirect('codemon:chat_invitation')

    # メールアドレスか数値かで処理を分ける
    member = None
    invited_email = None
    
    if '@' in identifier:
        # メールアドレスとして処理
        invited_email = identifier
        member = Account.objects.filter(email=identifier).first()
    else:
        # ユーザーIDとして処理（数値）
        try:
            user_id = int(identifier)
            member = Account.objects.filter(user_id=user_id).first()
            invited_email = member.email if member else identifier
        except ValueError:
            # 数値でもメールでもない場合はメールアドレスとして扱う
            invited_email = identifier

    # 招待リンクを作成
    token = uuid.uuid4().hex
    invite = MessegeGroupInvite.objects.create(
        group=group,
        invited_email=invited_email,
        invited_by=owner,
        token=token
    )

    invite_link = request.build_absolute_uri(
        reverse('codemon:messege_group_invite', args=[invite.token])
    )

    # 個別チャット（メールアドレス単位）に招待リンクを送信
    dm_thread, _ = DirectMessageThread.objects.get_or_create(
        owner=owner,
        participant_email=invited_email
    )
    DirectMessage.objects.create(
        thread=dm_thread,
        sender=owner,
        sender_label=owner.user_name,
        content=f"グループ『{group.group_name}』への招待リンク: {invite_link}"
    )

    messages.success(request, f'{invited_email}へ招待リンクを送信しました')
    return redirect('codemon:chat_teacher')


@session_login_required
def messege_group_invite(request, token):
    """招待リンクからメッセージグループに参加"""
    invite = MessegeGroupInvite.objects.filter(token=token, is_used=False).select_related('group', 'invited_by').first()
    if not invite:
        messages.error(request, '招待リンクが無効です')
        return redirect('accounts:karihome')

    user_id = request.session.get('account_user_id')
    account = Account.objects.filter(user_id=user_id).first() if user_id else None
    if not account:
        messages.error(request, 'ログインが必要です')
        return redirect('accounts:student_login')

    if account.email != invite.invited_email:
        messages.error(request, 'この招待リンクはあなた宛てではありません')
        return redirect('accounts:karihome')

    # GET時は確認画面を表示
    if request.method == 'GET':
        context = {
            'invite': invite,
            'group': invite.group,
            'invited_by': invite.invited_by,
            'member_count': MessegeMember.objects.filter(group=invite.group).count(),
        }
        return render(request, 'chat/invitation_confirm.html', context)

    # POST時はグループに参加
    if request.method == 'POST':
        if not MessegeMember.objects.filter(group=invite.group, member=account).exists():
            MessegeMember.objects.create(group=invite.group, member=account, role='student')

        invite.is_used = True
        invite.used_at = timezone.now()
        invite.save(update_fields=['is_used', 'used_at'])

        messages.success(request, f'グループ「{invite.group.group_name}」に参加しました')
        if account.type == 'teacher':
            return redirect('codemon:chat_teacher')
        return redirect('codemon:chat_student')



@session_login_required
def direct_messages(request, thread_id):
    """個別チャットのメッセージ送信・一覧取得（JSON）"""
    user_id = request.session.get('account_user_id')
    account = Account.objects.filter(user_id=user_id).first() if user_id else None
    if not account:
        return JsonResponse({'error': 'unauthorized'}, status=403)

    thread = DirectMessageThread.objects.filter(thread_id=thread_id).first()
    if not thread:
        return JsonResponse({'error': 'not_found'}, status=404)

    if not (thread.owner_id == account.user_id or thread.participant_email == account.email):
        return JsonResponse({'error': 'forbidden'}, status=403)

    if request.method == 'POST':
        # メッセージ送信
        import json
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()
            if not content:
                return JsonResponse({'error': 'メッセージが空です'}, status=400)
            
            # メッセージを作成
            message = DirectMessage.objects.create(
                thread=thread,
                sender=account,
                content=content
            )
            
            # スレッドの更新日時を更新
            thread.updated_at = message.created_at
            thread.save(update_fields=['updated_at'])
            
            return JsonResponse({
                'status': 'ok',
                'message': {
                    'message_id': message.message_id,
                    'sender_user_id': account.user_id,
                    'sender_name': account.user_name,
                    'sender_avatar': account.avatar.url if account.avatar else None,
                    'content': message.content,
                    'created_at': message.created_at.isoformat(),
                }
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': '不正なリクエスト'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    # GETリクエスト：メッセージ一覧を取得
    messages_qs = thread.messages.select_related('sender').all()
    data = []
    for msg in messages_qs:
        data.append({
            'id': msg.message_id,
            'message_id': msg.message_id,  # 互換性のため両方提供
            'content': msg.content,
            'created_at': msg.created_at.isoformat(),
            'sender_user_id': msg.sender.user_id if msg.sender else None,
            'sender_name': msg.sender.user_name if msg.sender else (msg.sender_label or 'system'),
            'sender_avatar': msg.sender.avatar.url if msg.sender and msg.sender.avatar else None
        })

    return JsonResponse({'thread_id': thread.thread_id, 'messages': data})


def grades_view_student(request):
    """生徒側点数閲覧"""
    return render(request, 'chat/grades_view_student.html')


@teacher_login_required
def submission_box_teacher(request, group_id=None):
    """教師側投函ボックス管理（グループごと）"""
    owner = _get_write_owner(request)
    boxes = []
    group = None
    
    if owner is not None:
        if group_id:
            # 特定のグループの投函ボックスのみを表示
            # グループが見つからない場合はリダイレクト
            try:
                group = MessegeGroup.objects.get(group_id=group_id, is_active=True)
            except MessegeGroup.DoesNotExist:
                messages.warning(request, 'グループが見つかりません')
                return redirect('codemon:submission_box')
            
            # 投函ボックスは作成者で制限（自分が作成したもののみ表示）
            # グループチャット用スレッドではなく、投函ボックス用スレッドのみを取得
            boxes = ChatThread.objects.filter(
                created_by=owner,
                group=group,
                is_active=True,
                title__startswith='投函ボックス：'
            ).order_by('-created_at')
        else:
            # グループが指定されていない場合は、グループがないボックスを表示
            # グループチャット用スレッドではなく、投函ボックス用スレッドのみを取得
            boxes = ChatThread.objects.filter(
                created_by=owner,
                is_active=True,
                title__startswith='投函ボックス：'
            ).order_by('-created_at')
    
    today = date.today()
    for box in boxes:
        box.deadline_date = _extract_deadline_from_thread(box)
        box.is_expired = bool(box.deadline_date and box.deadline_date < today)

    return render(request, 'chat/submission_box_management_teacher.html', {
        'boxes': boxes,
        'group': group,
        'group_id': group_id
    })


@teacher_login_required
def submission_box_create_teacher(request):
    """教師側投函ボックス新規作成"""
    if request.method == 'POST':
        # フォーム送信時の処理
        name = request.POST.get('box_name', '').strip()
        description = request.POST.get('box_description', '').strip()
        deadline = request.POST.get('box_deadline', '')
        group_id = request.POST.get('box_group', '')
        allow_multiple = request.POST.get('allow_multiple', 'off') == 'on'
        
        if name and deadline and group_id:
            try:
                # グループを取得
                group = MessegeGroup.objects.get(group_id=group_id)
                account = Account.objects.get(user_id=request.session.get('account_user_id'))
                
                # チャットスレッドを作成（投函ボックス用）
                thread = ChatThread.objects.create(
                    title=f"投函ボックス：{name}",
                    description=description,
                    created_by=account,
                    group=group
                )
                
                # グループチャットへの自動投稿は行わない
                
                # セッションに投函ボックス作成情報を保存（チャット画面での表示用）
                request.session['submission_box_created'] = {
                    'thread_id': thread.thread_id,
                    'box_title': thread.title,
                    'group_id': group_id
                }
                
                next_url = request.POST.get('next')
                if next_url:
                    return redirect(next_url)
                # 投函ボックス一覧画面へリダイレクト（グループなし）
                return redirect('codemon:submission_box')
            except MessegeGroup.DoesNotExist:
                pass
            except Account.DoesNotExist:
                pass
            except Exception as e:
                print(f"投函ボックス作成エラー: {e}")
    
    # 自分が参加しているメッセージグループを取得（所有者または メンバーとして参加しているグループ）
    user_id = request.session.get('account_user_id')
    account = Account.objects.filter(user_id=user_id).first() if user_id else None
    
    groups = []
    if account:
        # 自分が所有しているグループ
        owned_groups = MessegeGroup.objects.filter(owner=account, is_active=True)
        # 自分がメンバーとして参加しているグループ
        memberships = MessegeMember.objects.filter(member=account, is_active=True).select_related('group')
        member_groups = [m.group for m in memberships if m.group and m.group.is_active]
        # 重複を排除して結合
        groups = list(owned_groups) + [g for g in member_groups if g not in owned_groups]
    
    return render(request, 'chat/submission_box_create_teacher.html', {
        'groups': groups
    })


@teacher_login_required
def submission_box_delete_teacher(request, thread_id):
    """投函ボックス削除（論理削除）"""
    owner = _get_write_owner(request)
    if owner is None or getattr(owner, 'type', '') != 'teacher':
        messages.error(request, '教師権限が必要です')
        return redirect('codemon:submission_box')

    box = get_object_or_404(ChatThread, thread_id=thread_id, created_by=owner, is_active=True)

    if request.method == 'POST':
        box_title = box.title
        submission_count = box.messages.filter(is_deleted=False).count()

        box.is_active = False
        box.save()

        ChatMessage.objects.filter(thread=box).update(is_deleted=True)

        request.session['submission_box_delete_info'] = {
            'box_title': box_title,
            'submission_count': submission_count,
            'deleted_at': timezone.now().isoformat()
        }

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})

        return redirect('codemon:submission_box_delete_complete')

    return render(request, 'chat/submission_box_delete_teacher.html', {'box': box})


@session_login_required
def submission_box_detail(request, thread_id):
    """投函ボックス詳細画面（投稿閲覧・投稿）"""
    owner = _get_write_owner(request)
    if owner is None:
        messages.error(request, 'ログインが必要です')
        return redirect('accounts:student_login')
    
    box = get_object_or_404(ChatThread, thread_id=thread_id, is_active=True)
    
    deadline_date = _extract_deadline_from_thread(box)
    is_expired = bool(deadline_date and deadline_date < date.today())

    # POSTリクエストの場合（投稿処理）
    if request.method == 'POST':
        if is_expired:
            return HttpResponseForbidden('期限切れのため投稿できません')
        content = request.POST.get('content', '').strip()
        
        if content:
            # メッセージを作成
            message = ChatMessage.objects.create(
                thread=box,
                sender=owner,
                content=content
            )
            
            # 添付ファイルの処理
            files = request.FILES.getlist('attachments')
            for file in files:
                ChatAttachment.objects.create(
                    message=message,
                    file=file
                )
            
            # AJAXリクエストの場合はJSONを返す
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message_id': message.message_id})
            
            # 通常のPOSTの場合はリダイレクト
            return redirect('codemon:submission_box_detail', thread_id=thread_id)
    
    # 投稿一覧を取得
    submissions = box.messages.filter(is_deleted=False).select_related('sender').prefetch_related('attachments').order_by('created_at')
    
    is_teacher = getattr(owner, 'type', '') == 'teacher'

    return render(request, 'chat/submission_box_detail.html', {
        'box': box,
        'submissions': submissions,
        'is_teacher': is_teacher,
        'deadline_date': deadline_date,
        'is_expired': is_expired,
    })


@teacher_login_required
def submission_box_delete_complete(request):
    """投函ボックス削除完了画面"""
    owner = _get_write_owner(request)
    if owner is None or getattr(owner, 'type', '') != 'teacher':
        return redirect('codemon:submission_box')

    delete_info = request.session.pop('submission_box_delete_info', {})
    if not delete_info:
        return redirect('codemon:submission_box')

    return render(request, 'chat/submission_box_delete_complete_teacher.html', {
        'box_title': delete_info.get('box_title', ''),
        'submission_count': delete_info.get('submission_count', 0),
        'deleted_at': delete_info.get('deleted_at', '')
    })


@teacher_login_required
def group_management_teacher(request):
    """教師側グループ管理"""
    user_id = request.session.get('account_user_id')
    groups = []
    if user_id:
        account = Account.objects.filter(user_id=user_id).first()
        if account:
            groups = MessegeGroup.objects.filter(owner=account, is_active=True)
    return render(request, 'chat/messege_group_management_teacher.html', {'groups': groups})


@teacher_login_required
def chat_messege_group_create(request):
    """教師側メッセージグループ作成"""
    return render(request, 'chat/chat_messege_group_create.html')


@teacher_login_required
@require_POST
def messege_group_create(request):
    """教師側メッセージグループ作成（POST）"""
    user_id = request.session.get('account_user_id')
    account = Account.objects.filter(user_id=user_id).first() if user_id else None
    if not account:
        messages.error(request, 'アカウント情報が見つかりません')
        return redirect('accounts:teacher_login')

    group_name = request.POST.get('group_name', '').strip()
    group_password = request.POST.get('group_password', '').strip()

    if not group_name:
        messages.error(request, 'グループ名を入力してください')
        return redirect('codemon:chat_messege_group_create')

    group = MessegeGroup.objects.create(
        group_name=group_name,
        password=group_password or None,
        owner=account,
        description='',
        is_active=True
    )

    MessegeMember.objects.get_or_create(
        group=group,
        member=account,
        defaults={'role': 'teacher'}
    )

    messages.success(request, f'メッセージグループ「{group_name}」を作成しました')
    return redirect('codemon:group_management')


@teacher_login_required
def toggle_grading_check(request, message_id):
    """採点済みチェックボックスのトグル"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST method required'}, status=400)
    
    teacher = _get_write_owner(request)
    if teacher is None:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
    
    try:
        message = ChatMessage.objects.get(message_id=message_id)
        is_checked = request.POST.get('is_checked') == 'true'
        
        # 既存のスコアを取得または作成
        score, created = ChatScore.objects.get_or_create(
            message=message,
            defaults={'scorer': teacher, 'is_checked': is_checked}
        )
        
        if not created:
            score.is_checked = is_checked
            score.save()
        
        return JsonResponse({'status': 'success', 'is_checked': score.is_checked})
    except ChatMessage.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Message not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@session_login_required
def mark_messages_read(request):
    """メッセージを既読にする"""
    print(f"[DEBUG] mark_messages_read called: method={request.method}, user={request.user}, path={request.path}")
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST method required'}, status=400)
    
    reader = _get_write_owner(request)
    if reader is None:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
    
    try:
        import json
        data = json.loads(request.body)
        message_ids = data.get('message_ids', [])
        
        if not message_ids:
            return JsonResponse({'status': 'error', 'message': 'message_ids required'}, status=400)
        
        # 既読レコードを作成（自分以外のメッセージのみ）
        from .models import ReadReceipt
        created_count = 0
        print(f"[DEBUG] mark_messages_read: reader.user_id={reader.user_id}, message_ids={message_ids}")
        for message_id in message_ids:
            try:
                message = ChatMessage.objects.get(message_id=message_id, is_deleted=False)
                print(f"[DEBUG] message_id={message_id}, sender={message.sender.user_id}, reader={reader.user_id}")
                # 自分のメッセージは既読マークしない
                if message.sender.user_id != reader.user_id:
                    # 既に既読マークがある場合は作成しない
                    _, created = ReadReceipt.objects.get_or_create(
                        message=message,
                        reader=reader
                    )
                    print(f"[DEBUG] ReadReceipt created={created}")
                    if created:
                        created_count += 1
                else:
                    print(f"[DEBUG] Skipped: own message")
            except ChatMessage.DoesNotExist:
                print(f"[DEBUG] ChatMessage.DoesNotExist: message_id={message_id}")
                continue
        
        return JsonResponse({
            'status': 'success',
            'marked_count': created_count
        })
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"[ERROR] mark_messages_read: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@teacher_login_required
def grading_teacher(request, message_id=None):
    """教師側採点管理"""
    teacher = _get_write_owner(request)
    if teacher is None:
        return redirect('accounts:teacher_login')
    
    message = None
    existing_score = None
    
    # メッセージIDが指定されている場合は取得
    if message_id:
        try:
            message = ChatMessage.objects.select_related('sender', 'thread').prefetch_related('attachments').get(message_id=message_id)
            # 既存の採点情報を取得
            existing_score = ChatScore.objects.filter(message=message).first()
        except ChatMessage.DoesNotExist:
            messages.error(request, '指定された提出課題が見つかりません')
            return redirect('codemon:submission_box_teacher')
    
    if request.method == 'POST':
        if not message:
            messages.error(request, '提出課題が指定されていません')
            return redirect('codemon:submission_box_teacher')
        
        score_value = request.POST.get('score')
        good_points = request.POST.get('good_points', '').strip()
        improvement_points = request.POST.get('improvement_points', '').strip()
        advice = request.POST.get('advice', '').strip()
        
        if existing_score:
            # 既存の採点を更新
            existing_score.score = score_value
            existing_score.good_points = good_points
            existing_score.improvement_points = improvement_points
            existing_score.advice = advice
            existing_score.save()
            messages.success(request, '採点を更新しました')
        else:
            # 新規採点を保存
            ChatScore.objects.create(
                message=message,
                scorer=teacher,
                score=score_value,
                good_points=good_points,
                improvement_points=improvement_points,
                advice=advice
            )
            messages.success(request, '採点を保存しました')
        
        # 投函ボックス詳細画面に戻る
        return redirect('codemon:submission_box_detail', thread_id=message.thread.thread_id)
    
    context = {
        'message': message,
        'existing_score': existing_score,
    }
    return render(request, 'chat/grading_teacher.html', context)


@teacher_login_required
def grading_detail_view(request, message_id):
    """採点詳細確認画面"""
    teacher = _get_write_owner(request)
    if teacher is None:
        return redirect('accounts:teacher_login')
    
    try:
        message = ChatMessage.objects.select_related('sender', 'thread').prefetch_related('attachments').get(message_id=message_id)
        score = ChatScore.objects.filter(message=message).first()
    except ChatMessage.DoesNotExist:
        messages.error(request, '指定された提出課題が見つかりません')
        return redirect('codemon:submission_box_teacher')
    
    context = {
        'score': score,
        'is_teacher': True,
    }
    return render(request, 'chat/grading_detail_view.html', context)


@session_login_required
def grading_detail_student(request, message_id):
    """生徒側の採点詳細確認画面"""
    owner = _get_write_owner(request)
    if owner is None:
        messages.error(request, 'ログインが必要です')
        return redirect('accounts:student_login')

    try:
        message = ChatMessage.objects.select_related('sender', 'thread').prefetch_related('attachments').get(
            message_id=message_id,
            sender=owner
        )
        score = ChatScore.objects.filter(message=message).first()
    except ChatMessage.DoesNotExist:
        messages.error(request, '指定された提出課題が見つかりません')
        return redirect('codemon:submission_list_student')

    context = {
        'score': score,
        'is_teacher': False,
    }
    return render(request, 'chat/grading_detail_view.html', context)



@session_login_required
def submission_list_student(request):
    """生徒側提出課題一覧"""
    owner = _get_write_owner(request)
    if owner is None:
        messages.error(request, 'ログインが必要です')
        return redirect('accounts:student_login')
    
    # 生徒が投稿したメッセージ（投函ボックスへの投稿のみ）を取得
    # グループチャット（title='group_chat:*'）は除外し、投函ボックス（title='投函ボックス：*'）のみを対象とする
    submissions = ChatMessage.objects.filter(
        sender=owner,
        is_deleted=False,
        thread__title__startswith='投函ボックス：'
    ).select_related('thread', 'thread__group', 'sender').prefetch_related('attachments').order_by('-created_at')
    
    return render(request, 'chat/submission_list_student.html', {
        'submissions': submissions
    })


def chat_demo_index(request):
    """チャット機能デモインデックス"""
    return render(request, 'chat/index.html')


