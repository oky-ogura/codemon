import os
import json
from functools import wraps
from django.shortcuts import render, get_object_or_404, redirect
from django.db import models
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
    """Account を返すヘルパ。
    優先順: セッションの account_user_id -> request.user.email で Account を検索。
    匿名許可時は開発用アカウントを返す。
    """
    # 1) セッション優先
    uid = request.session.get('account_user_id')
    if uid:
        try:
            return Account.objects.get(user_id=uid)
        except Account.DoesNotExist:
            pass
    # 2) Djangoユーザーからメールで対応するAccountを探す
    if getattr(request, 'user', None) and getattr(request.user, 'is_authenticated', False):
        email = getattr(request.user, 'email', None)
        if email:
            acc = Account.objects.filter(email=email).first()
            if acc:
                return acc
    # 3) 匿名許可の開発用
    if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
        acct, _ = Account.objects.get_or_create(
            email='dev_anonymous@local',
            defaults={'user_name': '開発用匿名', 'password': 'dev', 'account_type': 'dev'}
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
	# Placeholder chat page; AI integration can be added later
	return render(request, 'codemon/chat.html')


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
            return redirect('accounts:student_login')
        checklists = Checklist.objects.filter(user=owner)
    return render(request, 'codemon/checklist_selection.html', {'checklists': checklists})

def checklist_list(request):
    """作成済みチェックリストの一覧を表示"""
    if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
        checklists = Checklist.objects.all().order_by('-updated_at')
    else:
        owner = _get_write_owner(request)
        if owner is None:
            return redirect('accounts:student_login')
        checklists = Checklist.objects.filter(user=owner).order_by('-updated_at')
    return render(request, 'codemon/checklist_list.html', {'checklists': checklists})

def checklist_create(request):
	if request.method == 'POST':
		owner = _get_write_owner(request)
		if owner is None:
			from django.urls import reverse
			login_url = reverse('accounts:student_login') + '?next=' + request.path
			messages.error(request, 'チェックリストの作成はログインが必要です。ログインしてください。')
			return redirect(login_url)

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
			return redirect('accounts:student_login')
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
			return redirect('accounts:student_login')
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
            return redirect('accounts:student_login')
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
			return redirect('accounts:student_login')
		cl = get_object_or_404(Checklist, checklist_id=pk, user=owner)
	return render(request, 'codemon/checklist_delete_confirm.html', {'checklist': cl})


def checklist_delete(request, pk):
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

    return render(request, 'codemon/group_list.html', {
        'groups': groups,
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
            return redirect('codemon:group_detail', group_id=group.group_id)

    return render(request, 'codemon/group_edit.html', {'group': group})


@require_POST
def group_delete(request, group_id):
    """グループの削除（論理削除）"""
    owner = _get_write_owner(request)
    if owner is None or owner.type != 'teacher':
        return HttpResponseForbidden('教師権限が必要です')

    group = get_object_or_404(Group, group_id=group_id, owner=owner, is_active=True)
    
    # グループを非アクティブ化（論理削除）
    group.is_active = False
    group.save()

    # メンバーシップも非アクティブ化
    GroupMember.objects.filter(group=group).update(is_active=False)

    # If called via AJAX, return JSON so front-end can update without redirect
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok', 'group_id': group_id, 'message': f'グループ「{group.group_name}」を削除しました'})

    messages.success(request, f'グループ「{group.group_name}」を削除しました')
    return redirect('codemon:group_list')


# If ALLOW_ANONYMOUS_VIEWS is False, wrap the view callables with the real
# login_required decorator so the production behavior is preserved. When the
# flag is True (development), views are left undecorated so anonymous access
# is allowed.
if not getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
    # Django標準の login_required ではなく、セッションベース認証も許可するカスタムを適用
    systems_list = session_login_required(systems_list)
    algorithms_list = session_login_required(algorithms_list)
    chat_view = session_login_required(chat_view)
    checklist_selection = session_login_required(checklist_selection)
    checklist_create = session_login_required(checklist_create)
    checklist_detail = session_login_required(checklist_detail)
    checklist_toggle_item = session_login_required(checklist_toggle_item)
    checklist_save = session_login_required(checklist_save)
    checklist_delete_confirm = session_login_required(checklist_delete_confirm)
    checklist_delete = session_login_required(checklist_delete)
    score_thread = session_login_required(score_thread)
    get_thread_readers = session_login_required(get_thread_readers)
    # グループ管理関連のビュー
    group_list = session_login_required(group_list)
    group_create = session_login_required(group_create)
    group_detail = session_login_required(group_detail)
    group_edit = session_login_required(group_edit)
    group_invite = session_login_required(group_invite)
    group_remove_member = session_login_required(group_remove_member)
    group_leave = session_login_required(group_leave)

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
    reply = chat_gemini(message, pairs, character_id=character)

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