"""
既存ユーザーに不正解システムを追加するスクリプト
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
from codemon.models import System

def add_incorrect_systems():
    print("=" * 80)
    print("既存ユーザーに不正解システムを追加")
    print("=" * 80)
    
    # 正解システムはあるが不正解システムがないユーザーを検索
    users_with_correct = System.objects.filter(system_name="正解").values_list('user_id', flat=True).distinct()
    users_with_incorrect = System.objects.filter(system_name="不正解").values_list('user_id', flat=True).distinct()
    
    users_need_incorrect = set(users_with_correct) - set(users_with_incorrect)
    
    print(f"\n不正解システムが必要なユーザー数: {len(users_need_incorrect)}")
    
    if not users_need_incorrect:
        print("✅ すべてのユーザーに不正解システムが存在します")
        return
    
    for user_id in users_need_incorrect:
        try:
            user = Account.objects.get(user_id=user_id)
            print(f"\n処理中: {user.user_name} (ID={user.user_id})")
            
            # 不正解システムを作成
            incorrect_system, created = System.objects.get_or_create(
                user=user,
                system_name="不正解",
                defaults={
                    'system_description': "チュートリアル用の不正解画面"
                }
            )
            
            if created:
                print(f"  ✅ 不正解システムを作成しました (ID={incorrect_system.system_id})")
            else:
                print(f"  ℹ️ 不正解システムは既に存在します (ID={incorrect_system.system_id})")
                
        except Account.DoesNotExist:
            print(f"  ❌ ユーザーID={user_id} が見つかりません")
        except Exception as e:
            print(f"  ❌ エラー: {e}")
    
    print("\n" + "=" * 80)
    print("完了！")
    print("=" * 80)

if __name__ == '__main__':
    add_incorrect_systems()
