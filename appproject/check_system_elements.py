import os
import django

# Django設定を読み込む
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from codemon.models import System, SystemElement

# すべてのシステムとその要素を表示
systems = System.objects.all()
print(f"=== システム一覧 (全{systems.count()}件) ===\n")

for system in systems:
    print(f"システムID: {system.system_id}")
    print(f"システム名: {system.system_name}")
    print(f"ユーザー: {system.user.user_id}")
    print(f"作成日時: {system.created_at}")
    
    elements = SystemElement.objects.filter(system=system).order_by('sort_order')
    print(f"\n  要素 (全{elements.count()}件):")
    
    if elements.count() == 0:
        print("    (要素なし)")
    else:
        for elem in elements:
            print(f"    - タイプ: {elem.element_type}")
            print(f"      ラベル: '{elem.element_label}'")
            print(f"      値: '{elem.element_value}'")
            print(f"      位置: ({elem.position_x}, {elem.position_y})")
            print()
    
    print("-" * 60)
    print()
