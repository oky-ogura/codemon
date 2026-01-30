import json
from functools import wraps
from django.shortcuts import render, get_object_or_404, redirect
from django.db import models
from django.contrib import messages
from django.conf import settings
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
    Group, GroupMember, AIConversation, AIMessage
)
from accounts.models import Account
from django.utils import timezone
from django.db.models import Q
from django.db import transaction

# 実績システムのビューをインポート
from .views_achievements import achievements_view, claim_achievement_reward, clear_achievement_notifications


# _get_write_owner: セッションまたはrequest.userからAccountを取得
def _get_write_owner(request):
    """
    セッションからAccount（ユーザー）を取得。なければrequest.user（Django認証）を返す。
    """
    try:
        uid = request.session.get('account_user_id')
        if uid:
            return Account.objects.filter(user_id=uid).first()
    except Exception:
        pass
    if getattr(request, 'user', None) and getattr(request.user, 'is_authenticated', False):
        return request.user
    return None



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
	認証されていない場合、教師ログインページにリダイレクトします。
	"""
	@wraps(view_func)
	def _wrapped_view(request, *args, **kwargs):
		if not request.session.get('is_account_authenticated'):
			return redirect('accounts:teacher_login')
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
            return JsonResponse({'status': 'ok', 'is_done': item.is_done})
        # is_doneがboolでない場合は反転（従来互換）
    except Exception:
        pass

    # フォールバック: 反転(従来のフォームPOST用)
    item.is_done = not item.is_done
    item.save()
    return redirect('codemon:checklist_detail', pk=pk)


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
    context = {
        'checklists': checklists,
        'account': owner,  # Account オブジェクトをテンプレートで使用可能に
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

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        if name:
            cl = Checklist.objects.create(user=owner, checklist_name=name, checklist_description=description)

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

            messages.success(request, 'チェックリストを作成しました。')
            return redirect('codemon:checklist_detail', pk=cl.checklist_id)
    return render(request, 'codemon/checklist_create.html', {'user': owner})


def checklist_detail(request, pk):
	owner = _get_write_owner(request)
	if owner is None:
		return redirect('accounts:student_login')
	
	if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
		cl = get_object_or_404(Checklist, checklist_id=pk)
	else:
		cl = get_object_or_404(Checklist, checklist_id=pk, user=owner)
	if request.method == 'POST':
		# new item
		text = request.POST.get('item_text')
		if text:
			max_order = cl.items.aggregate(models.Max('sort_order'))['sort_order__max'] or 0
			ChecklistItem.objects.create(checklist=cl, item_text=text, sort_order=max_order + 1)
			return redirect('codemon:checklist_detail', pk=pk)
	return render(request, 'codemon/checklist_detail.html', {'checklist': cl})




def checklist_edit(request, pk):
    if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
        cl = get_object_or_404(Checklist, checklist_id=pk)
    else:
        cl = get_object_or_404(Checklist, checklist_id=pk, user=request.user)
    return render(request, 'codemon/checklist_edit.html', {'checklist': cl})

def checklist_save(request, pk):
    checklist = get_object_or_404(Checklist, checklist_id=pk)
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
	if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
		cl = get_object_or_404(Checklist, checklist_id=pk)
	else:
		cl = get_object_or_404(Checklist, checklist_id=pk, user=request.user)
	return render(request, 'codemon/checklist_delete_confirm.html', {'checklist': cl})


def checklist_delete(request, pk):
    if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
        cl = get_object_or_404(Checklist, checklist_id=pk)
    else:
        cl = get_object_or_404(Checklist, checklist_id=pk, user=request.user)

    if request.method == 'POST':
        deleted_pk = cl.checklist_id
        deleted_name = cl.checklist_name
        deleted_description = getattr(cl, 'checklist_description', '')
        deleted_items = list(cl.items.values('checklist_item_id', 'item_text', 'is_done'))
        items_count = len(deleted_items)
        cl.delete()
        messages.success(request,
            f'チェックリスト「{checklist_name}」と{items_count}個の項目が削除されました。')
        return render(request, 'codemon/checklist_delete_complete.html',
            {'deleted_name': checklist_name, 'deleted_items_count': items_count})
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
            return redirect('codemon:group_detail', group_id=group.group_id)

    return render(request, 'codemon/group_edit.html', {'group': group})


@require_POST
def group_delete(request, group_id):
    """グループの削除（論理削除）"""
    if request.method != 'POST':
        return HttpResponseForbidden('POSTメソッドが必要です')
    
    # セッションから現在のユーザーIDを取得
    current_user_id = request.session.get('account_user_id')
    if not current_user_id:
        messages.error(request, 'ログインが必要です')
        return redirect('accounts:account_entry')
    
    # グループを非アクティブ化（論理削除）
    group.is_active = False
    group.save()

    # メンバーシップも非アクティブ化
    GroupMember.objects.filter(group=group).update(is_active=False)

    messages.success(request, f'グループ「{group.group_name}」を削除しました')
    return redirect('codemon:group_list')


# If ALLOW_ANONYMOUS_VIEWS is False, wrap the view callables with the real
# login_required decorator so the production behavior is preserved. When the
# flag is True (development), views are left undecorated so anonymous access
# is allowed.
if not getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
    systems_list = _login_required(systems_list)
    algorithms_list = _login_required(algorithms_list)
    chat_view = _login_required(chat_view)
    # checklist_selection, checklist_list, checklist_create, checklist_detail は _get_write_owner で認証チェック済み
    # checklist_toggle_item = _login_required(checklist_toggle_item)  # ← account_or_login_required で認証判定するため不要
    checklist_save = _login_required(checklist_save)
    checklist_delete_confirm = _login_required(checklist_delete_confirm)
    checklist_delete = _login_required(checklist_delete)
    score_thread = _login_required(score_thread)
    get_thread_readers = _login_required(get_thread_readers)
    # グループ管理関連のビュー
    group_list = _login_required(group_list)
    group_create = _login_required(group_create)
    group_detail = _login_required(group_detail)
    group_edit = _login_required(group_edit)
    group_invite = _login_required(group_invite)
    # group_remove_member は @teacher_login_required デコレータを使用しているため、ここではラップしない
    group_leave = _login_required(group_leave)

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
<<<<<<< HEAD
    return redirect('codemon:accessory_shop')
=======

>>>>>>> main
# ========================================
# チャット機能 - 新しいUI画面
# ========================================

@login_required
@login_required
def chat_student(request):
    """生徒側チャット画面"""
    return render(request, 'chat/chat_student.html')


@login_required
def chat_teacher(request):
    """教師側チャット画面"""
    return render(request, 'chat/chat_teacher.html')


@login_required
def icon_settings_student(request):
    """生徒側アイコン設定"""
    return render(request, 'chat/icon_settings_student.html')


@login_required
def icon_settings_teacher(request):
    """教師側アイコン設定"""
    return render(request, 'chat/icon_settings_teacher.html')


@login_required
def upload_file_student(request):
    """生徒側ファイル投函"""
    return render(request, 'chat/upload_file_student.html')


@login_required
def upload_file_teacher(request):
    """教師側ファイル投函"""
    return render(request, 'chat/upload_file_teacher.html')


@login_required
def upload_image_student(request):
    """生徒側画像投函"""
    return render(request, 'chat/upload_image_student.html')


@login_required
def upload_image_teacher(request):
    """教師側画像投函"""
    return render(request, 'chat/upload_image_teacher.html')


@login_required
def grades_view_student(request):
    """生徒側点数閲覧"""
    return render(request, 'chat/grades_view_student.html')


@login_required
def submission_box_teacher(request):
    """教師側投函ボックス管理"""
    return render(request, 'chat/submission_box_teacher.html')


@login_required
def group_management_teacher(request):
    """教師側グループ管理"""
    return render(request, 'chat/group_management_teacher.html')


@login_required
def grading_teacher(request):
    """教師側採点管理"""
    return render(request, 'chat/grading_teacher.html')


@login_required
def chat_demo_index(request):
    """チャット機能デモインデックス"""
    return render(request, 'chat/index.html')
<<<<<<< HEAD
=======

>>>>>>> main
