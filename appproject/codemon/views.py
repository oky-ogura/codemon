from django.shortcuts import render, get_object_or_404, redirect
from django.db import models
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Checklist, ChecklistItem


@login_required
def systems_list(request):
	# placeholder: list systems belonging to user
	systems = []
	return render(request, 'codemon/systems_list.html', {'systems': systems})


@login_required
def algorithms_list(request):
	algorithms = []
	return render(request, 'codemon/algorithms_list.html', {'algorithms': algorithms})


@login_required
def chat_view(request):
	# Placeholder chat page; AI integration can be added later
	return render(request, 'codemon/chat.html')


@login_required
def checklist_list(request):
	qs = Checklist.objects.filter(user=request.user).order_by('-updated_at')
	return render(request, 'codemon/checklist_list.html', {'checklists': qs})


@login_required
def checklist_create(request):
	if request.method == 'POST':
		name = request.POST.get('name')
		description = request.POST.get('description', '')
		if name:
			cl = Checklist.objects.create(user=request.user, checklist_name=name, checklist_description=description)
			
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


@login_required
def checklist_detail(request, pk):
	cl = get_object_or_404(Checklist, checklist_id=pk, user=request.user)
	if request.method == 'POST':
		# new item
		text = request.POST.get('item_text')
		if text:
			max_order = cl.items.aggregate(models.Max('sort_order'))['sort_order__max'] or 0
			ChecklistItem.objects.create(checklist=cl, item_text=text, sort_order=max_order + 1)
			return redirect('codemon:checklist_detail', pk=pk)
	return render(request, 'codemon/checklist_detail.html', {'checklist': cl})


@login_required
@require_POST
def checklist_toggle_item(request, pk, item_id):
	cl = get_object_or_404(Checklist, checklist_id=pk, user=request.user)
	item = get_object_or_404(ChecklistItem, checklist=cl, checklist_item_id=item_id)
	item.is_done = not item.is_done
	item.save()
	return redirect('codemon:checklist_detail', pk=pk)


@login_required
def checklist_save(request, pk):
	cl = get_object_or_404(Checklist, checklist_id=pk, user=request.user)
	
	if request.method == 'POST':
		# 既存の項目を更新
		for key, value in request.POST.items():
			if key.startswith('item_id_'):
				item_id = key.replace('item_id_', '')
				item_text = request.POST.get(f'item_text_{item_id}', '').strip()
				
				if item_text:
					item = get_object_or_404(ChecklistItem, checklist=cl, checklist_item_id=item_id)
					item.item_text = item_text
					item.save()
		
		messages.success(request, '保存しました')
		return redirect('codemon:checklist_save', pk=pk)
	
	return render(request, 'codemon/checklist_save.html', {'checklist': cl})


@login_required
def checklist_delete_confirm(request, pk):
	cl = get_object_or_404(Checklist, checklist_id=pk, user=request.user)
	return render(request, 'codemon/checklist_delete_confirm.html', {'checklist': cl})


@login_required
def checklist_delete(request, pk):
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
