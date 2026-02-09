"""
user_id=1 のパスワードをリセット
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
from django.contrib.auth.hashers import make_password

def reset_password():
    print("=" * 60)
    print("user_id=1 のパスワードリセット")
    print("=" * 60)
    
    new_password = "newpassword123"
    
    try:
        user = Account.objects.get(user_id=1)
        print(f"\n📋 現在の情報:")
        print(f"   user_id: {user.user_id}")
        print(f"   user_name: {user.user_name}")
        print(f"   email: {user.email}")
        print(f"   account_type: {user.account_type}")
        
        # パスワードをハッシュ化して設定
        user.password = make_password(new_password)
        user.save()
        
        print(f"\n✅ パスワードをリセットしました")
        print(f"\n新しいログイン情報:")
        print(f"=" * 60)
        
        if user.account_type == 'teacher':
            print(f"URL: http://localhost:8000/accounts/teacher_login/")
        elif user.account_type == 'student':
            print(f"URL: http://localhost:8000/accounts/student_login/")
        else:
            print(f"⚠️ account_type: {user.account_type}")
        
        print(f"ユーザー名: {user.user_name}")
        print(f"パスワード: {new_password}")
        print("=" * 60)
        
    except Account.DoesNotExist:
        print("\n❌ user_id=1 のアカウントが見つかりません")
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reset_password()
