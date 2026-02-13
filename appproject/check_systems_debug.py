"""
システム表示問題のデバッグスクリプト
"""
import os
import sys
import django

# Django設定
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from accounts.models import Account
from codemon.models import System, SystemElement
from django.conf import settings

def check_systems():
    print("=" * 80)
    print("システム表示問題のデバッグ")
    print("=" * 80)
    
    # 0. 全ユーザーリストを表示
    print("\n【0】全ユーザーリスト:")
    all_users = Account.objects.all().order_by('user_id')
    print(f"  総ユーザー数: {all_users.count()}")
    for user in all_users:
        print(f"    - ID:{user.user_id}, 名前:'{user.user_name}', タイプ:{user.account_type}")
    
    # 1. テンプレートユーザー（rg）の確認
    print("\n【1】テンプレートユーザー（rg）の確認:")
    template_user = Account.objects.filter(user_name='rg').first()
    
    if template_user:
        print(f"  ✅ ユーザー名: {template_user.user_name}")
        print(f"  ✅ ユーザーID: {template_user.user_id}")
        print(f"  ✅ アカウントタイプ: {template_user.account_type}")
        
        # テンプレートユーザーのシステムを確認
        systems = System.objects.filter(user=template_user).order_by('system_name')
        print(f"\n  システム数: {systems.count()}")
        
        for sys in systems:
            try:
                elem_count = SystemElement.objects.filter(system=sys).count()
            except Exception as e:
                elem_count = f"エラー: {e}"
            print(f"    - ID:{sys.system_id}, 名前:'{sys.system_name}', 要素数:{elem_count}")
            print(f"      作成日: {sys.created_at}, 更新日: {sys.updated_at}")
    else:
        print("  ❌ テンプレートユーザー（rg）が見つかりません")
    
    # 2. 最新の登録ユーザーを確認
    print("\n【2】最新の登録ユーザー:")
    latest_users = Account.objects.exclude(user_name='rg').exclude(user_name='admin').order_by('-user_id')[:3]
    
    if latest_users.exists():
        for user in latest_users:
            print(f"\n  ユーザー名: {user.user_name} (ID: {user.user_id})")
            systems = System.objects.filter(user=user).order_by('system_name')
            print(f"  システム数: {systems.count()}")
            
            for sys in systems:
                try:
                    elem_count = SystemElement.objects.filter(system=sys).count()
                except Exception as e:
                    elem_count = f"エラー"
                print(f"    - ID:{sys.system_id}, 名前:'{sys.system_name}', 要素数:{elem_count}")
                print(f"      作成日: {sys.created_at}, 更新日: {sys.updated_at}")
    else:
        print("  ❌ 登録ユーザーが見つかりません")
    
    # 3. 「正解」「不正解」システムの統計
    print("\n【3】「正解」「不正解」システムの統計:")
    correct_systems = System.objects.filter(system_name="正解")
    incorrect_systems = System.objects.filter(system_name="不正解")
    
    print(f"  「正解」システム: {correct_systems.count()}個")
    print(f"  「不正解」システム: {incorrect_systems.count()}個")
    
    # 4. settings.pyのTUTORIAL_TEMPLATE_USER_IDを確認
    print("\n【4】設定ファイルの確認:")
    template_user_id = getattr(settings, 'TUTORIAL_TEMPLATE_USER_ID', None)
    print(f"  TUTORIAL_TEMPLATE_USER_ID: {template_user_id}")
    
    if template_user_id and template_user:
        if template_user.user_id == template_user_id:
            print(f"  ✅ 設定とデータが一致しています")
        else:
            print(f"  ⚠️  設定({template_user_id})とrgのユーザーID({template_user.user_id})が一致しません")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    check_systems()
