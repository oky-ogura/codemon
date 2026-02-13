"""
create_tutorial_systems関数のテスト
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
from accounts.views import create_tutorial_systems
from django.contrib.auth.hashers import make_password

def test_create_tutorial_systems():
    print("=" * 80)
    print("create_tutorial_systems関数のテスト")
    print("=" * 80)
    
    # テストユーザーを作成
    test_username = f"test_tutorial_{Account.objects.count() + 1}"
    
    try:
        test_user = Account.objects.create(
            user_name=test_username,
            email=f"{test_username}@example.com",
            password=make_password("testpass123"),
            account_type="student"
        )
        print(f"\n✅ テストユーザー作成: {test_user.user_name} (ID={test_user.user_id})")
        
        # create_tutorial_systems関数を実行
        print("\n📋 create_tutorial_systems関数を実行...")
        try:
            correct_sys, incorrect_sys = create_tutorial_systems(test_user)
            
            print(f"\n結果:")
            print(f"  正解システム: {correct_sys}")
            print(f"  不正解システム: {incorrect_sys}")
            
            # データベースから確認
            systems = System.objects.filter(user=test_user).order_by('system_name')
            print(f"\nデータベース上のシステム数: {systems.count()}")
            for sys in systems:
                print(f"  - ID:{sys.system_id}, 名前:'{sys.system_name}'")
                print(f"    説明: {sys.system_description}")
                
        except Exception as e:
            print(f"\n❌ エラー発生: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"\n❌ テストユーザー作成エラー: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    test_create_tutorial_systems()
