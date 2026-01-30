"""
新しいアクセサリーを装備してテストするスクリプト
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from codemon.models import Accessory, UserAccessory
from accounts.models import Account

def equip_new_accessory():
    """adminユーザーに新しいアクセサリーを装備"""
    
    # adminユーザーを取得
    admin = Account.objects.filter(user_name='admin').first()
    if not admin:
        print("❌ adminユーザーが見つかりません")
        return
    
    print(f"ユーザー: {admin.user_name} (ID: {admin.user_id})")
    print(f"キャラクター: {admin.appearance}\n")
    
    # 新しいアクセサリーから適切なものを選択
    # adminのキャラクターに合わせてアクセサリーを選ぶ
    character_map = {
        'イヌ.png': 'inu',
        'ウサギ.png': 'usagi',
        'キツネ.png': 'kitsune',
        'ネコ.png': 'neko',
        'パンダ.png': 'panda',
        'フクロウ.png': 'fukurou',
        'リス.png': 'risu',
        'アルパカ.png': 'alpaca',
    }
    
    char_type = character_map.get(admin.appearance, 'inu')
    
    # キャラクター別の花アクセサリーを検索
    flower_acc = Accessory.objects.filter(
        category='flower',
        css_class__contains=char_type
    ).first()
    
    if not flower_acc:
        print(f"❌ {char_type}用の花アクセサリーが見つかりません")
        return
    
    print(f"選択されたアクセサリー:")
    print(f"  名前: {flower_acc.name}")
    print(f"  カテゴリ: {flower_acc.category}")
    print(f"  CSS class: [{flower_acc.css_class}]\n")
    
    # 既存の装備を解除
    UserAccessory.objects.filter(user=admin, is_equipped=True).update(is_equipped=False)
    
    # 新しいアクセサリーを所有＆装備
    user_acc, created = UserAccessory.objects.get_or_create(
        user=admin,
        accessory=flower_acc,
        defaults={'is_equipped': True}
    )
    
    if not created:
        user_acc.is_equipped = True
        user_acc.save()
    
    print("✅ 装備完了！\n")
    
    # 確認
    equipped = UserAccessory.objects.filter(user=admin, is_equipped=True).select_related('accessory').first()
    if equipped:
        print("【現在の装備】")
        print(f"アクセサリー名: {equipped.accessory.name}")
        print(f"CSS class: [{equipped.accessory.css_class}]")
        print(f"\nHTMLで表示される内容:")
        print(f'<span class="character-accessory acc {equipped.accessory.css_class}"></span>')
        print(f"\n🌺 ページをリロード（Ctrl+Shift+R）して確認してください！")
    else:
        print("❌ 装備が確認できません")

if __name__ == '__main__':
    equip_new_accessory()
