"""
user_id=1 のアカウント情報を確認
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

def check_user_info():
    print("=" * 60)
    print("user_id=1 のアカウント情報")
    print("=" * 60)
    
    try:
        user = Account.objects.get(user_id=1)
        print(f"\n✅ アカウント検出:")
        print(f"   user_id: {user.user_id}")
        print(f"   user_name: {user.user_name}")
        print(f"   email: {user.email}")
        print(f"   account_type: {user.account_type}")
        print(f"   作成日時: {user.created_at}")
        
        # パスワードハッシュの形式確認
        if user.password:
            if user.password.startswith('pbkdf2_sha256'):
                print(f"   パスワード: ハッシュ化済み (Django形式)")
            else:
                print(f"   パスワード: 長さ{len(user.password)}文字 (形式要確認)")
        else:
            print(f"   パスワード: 未設定")
        
        print("\n" + "=" * 60)
        print("ログイン情報:")
        print("=" * 60)
        
        if user.account_type == 'teacher':
            print(f"\n教員用ログインページ:")
            print(f"  URL: http://localhost:8000/accounts/teacher_login/")
            print(f"  ユーザー名: {user.user_name}")
            print(f"  パスワード: (設定したパスワード)")
        elif user.account_type == 'student':
            print(f"\n生徒用ログインページ:")
            print(f"  URL: http://localhost:8000/accounts/student_login/")
            print(f"  ユーザー名: {user.user_name}")
            print(f"  パスワード: (設定したパスワード)")
        else:
            print(f"\n⚠️ account_type が '{user.account_type}' です")
            print(f"  teacher または student に変更する必要があるかもしれません")
        
    except Account.DoesNotExist:
        print("\n❌ user_id=1 のアカウントが見つかりません")
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_user_info()
