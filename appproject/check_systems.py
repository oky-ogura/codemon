"""
システムと要素の確認スクリプト
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from codemon.models import System, SystemElement

# すべてのシステムを表示
systems = System.objects.all().order_by('system_id')

print("=" * 80)
print("システム一覧")
print("=" * 80)

for system in systems:
    print(f"\nシステムID: {system.system_id}")
    print(f"  名前: {system.system_name}")
    print(f"  説明: {system.system_description or '(なし)'}")
    print(f"  作成日: {system.created_at}")
    
    # このシステムの要素を取得
    elements = SystemElement.objects.filter(system=system).order_by('sort_order', 'element_id')
    print(f"  要素数: {elements.count()}")
    
    if elements.exists():
        for elem in elements:
            print(f"    - [{elem.element_type}] {elem.element_label or '(ラベルなし)'}")
            if elem.element_type == 'button' and elem.element_config:
                config = elem.element_config
                print(f"      ボタンテキスト: {config.get('text', '(なし)')}")
                print(f"      アルゴリズムID: {config.get('algorithm_id', '(なし)')}")
    else:
        print("    (要素なし)")

print("\n" + "=" * 80)
