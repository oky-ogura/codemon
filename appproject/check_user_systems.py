#!/usr/bin/env python
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from codemon.models import System, SystemElement
from accounts.models import Account

# 新規ユーザーを探す（最新のユーザー）
users = Account.objects.exclude(user_name='rg').order_by('-user_id')[:3]
for user in users:
    print(f'\nユーザー: {user.user_name} (user_id: {user.user_id}, created: {user.created_at})')
    systems = System.objects.filter(user=user, system_name__in=['正解', '不正解']).order_by('system_name')
    for sys in systems:
        print(f'  {sys.system_name} (ID: {sys.system_id})')
        elements = SystemElement.objects.filter(system=sys).order_by('element_id')
        print(f'    要素数: {elements.count()}')
        for elem in elements:
            val = str(elem.element_value)[:20] if elem.element_value else ''
            label = elem.element_label if elem.element_label else '(ラベルなし)'
            print(f'      - {elem.element_type:15} | {label:20} | {val}')
