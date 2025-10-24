from django.shortcuts import render, get_object_or_404, redirect
from django.db import models
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required as _login_required
from django.views.decorators.http import require_POST
from .models import Checklist, ChecklistItem
from accounts.models import Account


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
	if getattr(request, 'user', None) and getattr(request.user, 'is_authenticated', False):
		return request.user
	if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
		acct, _ = Account.objects.get_or_create(
			email='dev_anonymous@local',
			defaults={'user_name': '開発用匿名', 'password': 'dev', 'type': 'dev'}
		)
		return acct
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


def checklist_list(request):
	if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
		qs = Checklist.objects.all().order_by('-updated_at')
	else:
		qs = Checklist.objects.filter(user=request.user).order_by('-updated_at')
	return render(request, 'codemon/checklist_list.html', {'checklists': qs})


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
		cl = get_object_or_404(Checklist, checklist_id=pk, user=request.user)
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
		cl = get_object_or_404(Checklist, checklist_id=pk, user=request.user)
	item = get_object_or_404(ChecklistItem, checklist=cl, checklist_item_id=item_id)
	item.is_done = not item.is_done
	item.save()
	return redirect('codemon:checklist_detail', pk=pk)


def checklist_edit(request, pk):
    if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
        cl = get_object_or_404(Checklist, checklist_id=pk)
    else:
        cl = get_object_or_404(Checklist, checklist_id=pk, user=request.user)
    return render(request, 'codemon/checklist_edit.html', {'checklist': cl})


def checklist_save(request, pk):
    if getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
        cl = get_object_or_404(Checklist, checklist_id=pk)
    else:
        cl = get_object_or_404(Checklist, checklist_id=pk, user=request.user)
    
    if request.method == 'POST':
        # チェックリストの基本情報を更新
        cl.checklist_name = request.POST.get('checklist_name', cl.checklist_name)
        cl.checklist_description = request.POST.get('checklist_description', cl.checklist_description)
        cl.save()

        # 既存の項目を更新または削除
        submitted_ids = []
        item_ids = request.POST.getlist('item_ids[]')
        item_texts = request.POST.getlist('item_texts[]')
        
        for i, item_id in enumerate(item_ids):
            if item_id and item_texts[i].strip():
                item = get_object_or_404(ChecklistItem, checklist=cl, checklist_item_id=item_id)
                item.item_text = item_texts[i].strip()
                item.save()
                submitted_ids.append(int(item_id))

        # 送信されなかった既存の項目を削除
        cl.items.exclude(checklist_item_id__in=submitted_ids).delete()

        # 新しい項目を追加
        new_texts = request.POST.getlist('new_item_texts[]')
        max_order = cl.items.aggregate(models.Max('sort_order'))['sort_order__max'] or 0
        
        for i, text in enumerate(new_texts):
            if text.strip():
                ChecklistItem.objects.create(
                    checklist=cl,
                    item_text=text.strip(),
                    sort_order=max_order + i + 1
                )

        messages.success(request, 'チェックリストを保存しました')
        return redirect('codemon:checklist_detail', pk=pk)
    
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
        checklist_name = cl.checklist_name
        items_count = cl.items.count()
        cl.delete()
        messages.success(request,
            f'チェックリスト「{checklist_name}」と{items_count}個の項目が削除されました。')
        return render(request, 'codemon/checklist_delete_complete.html',
            {'deleted_name': checklist_name, 'deleted_items_count': items_count})

    return redirect('codemon:checklist_delete_confirm', pk=pk)


# If ALLOW_ANONYMOUS_VIEWS is False, wrap the view callables with the real
# login_required decorator so the production behavior is preserved. When the
# flag is True (development), views are left undecorated so anonymous access
# is allowed.
if not getattr(settings, 'ALLOW_ANONYMOUS_VIEWS', False):
    systems_list = _login_required(systems_list)
    algorithms_list = _login_required(algorithms_list)
    chat_view = _login_required(chat_view)
    checklist_list = _login_required(checklist_list)
    checklist_create = _login_required(checklist_create)
    checklist_detail = _login_required(checklist_detail)
    checklist_toggle_item = _login_required(checklist_toggle_item)
    checklist_save = _login_required(checklist_save)
    checklist_delete_confirm = _login_required(checklist_delete_confirm)
    checklist_delete = _login_required(checklist_delete)
