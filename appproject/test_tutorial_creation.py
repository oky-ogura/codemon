"""
チュートリアルシステム自動作成機能のテストスクリプト
Python環境: python test_tutorial_creation.py
"""
import os
import django
import sys

# Djangoプロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Django設定を読み込む
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from accounts.models import Account
from codemon.models import System, SystemElement
from accounts.views import create_tutorial_systems

def test_tutorial_systems_creation():
    """
    チュートリアルシステム作成機能のテスト
    """
    print("=" * 60)
    print("チュートリアルシステム作成機能テスト")
    print("=" * 60)
    
    # テスト用ユーザーを作成（または既存ユーザーを使用）
    test_user_email = "test_tutorial_user@example.com"
    
    # 既存のテストユーザーを削除（クリーンな状態でテスト）
    try:
        existing_user = Account.objects.filter(email=test_user_email).first()
        if existing_user:
            print(f"\n既存のテストユーザーを削除: {existing_user.user_name}")
            # 関連するシステムも削除される（CASCADE）
            existing_user.delete()
    except Exception as e:
        print(f"⚠️ 既存ユーザー削除エラー: {e}")
    
    # 新しいテストユーザーを作成
    try:
        test_user = Account.objects.create(
            email=test_user_email,
            user_name="テストユーザー",
            password="hashed_password",  # 実際はハッシュ化が必要
            age=10,
            account_type="student"
        )
        print(f"\n✅ テストユーザー作成成功: {test_user.user_name} (ID: {test_user.user_id})")
    except Exception as e:
        print(f"❌ テストユーザー作成失敗: {e}")
        return
    
    # チュートリアルシステムを作成
    print("\n" + "-" * 60)
    print("チュートリアルシステムを作成中...")
    print("-" * 60)
    
    try:
        correct_system, incorrect_system = create_tutorial_systems(test_user)
        
        if correct_system and incorrect_system:
            print("✅ チュートリアルシステム作成成功！")
            
            # 正解システムの確認
            print(f"\n【正解システム】")
            print(f"  - システムID: {correct_system.system_id}")
            print(f"  - システム名: {correct_system.system_name}")
            print(f"  - 説明: {correct_system.system_description}")
            
            correct_elements = SystemElement.objects.filter(system=correct_system)
            print(f"  - 要素数: {correct_elements.count()}")
            for elem in correct_elements:
                print(f"    └ タイプ: {elem.element_type}, ラベル: {elem.element_label}")
            
            # 不正解システムの確認
            print(f"\n【不正解システム】")
            print(f"  - システムID: {incorrect_system.system_id}")
            print(f"  - システム名: {incorrect_system.system_name}")
            print(f"  - 説明: {incorrect_system.system_description}")
            
            incorrect_elements = SystemElement.objects.filter(system=incorrect_system)
            print(f"  - 要素数: {incorrect_elements.count()}")
            for elem in incorrect_elements:
                print(f"    └ タイプ: {elem.element_type}, ラベル: {elem.element_label}")
            
            # 重複作成のテスト（get_or_createの動作確認）
            print("\n" + "-" * 60)
            print("重複作成テスト（2回目の呼び出し）...")
            print("-" * 60)
            
            correct_system2, incorrect_system2 = create_tutorial_systems(test_user)
            
            if correct_system.system_id == correct_system2.system_id:
                print("✅ 正解システムは重複作成されませんでした（get_or_createが正常動作）")
            else:
                print("⚠️ 正解システムが重複作成されました")
            
            if incorrect_system.system_id == incorrect_system2.system_id:
                print("✅ 不正解システムは重複作成されませんでした（get_or_createが正常動作）")
            else:
                print("⚠️ 不正解システムが重複作成されました")
            
        else:
            print("❌ チュートリアルシステム作成失敗")
    except Exception as e:
        print(f"❌ エラー発生: {e}")
        import traceback
        traceback.print_exc()
    
    # クリーンアップ（テストデータの削除）
    print("\n" + "-" * 60)
    print("テストデータをクリーンアップ中...")
    print("-" * 60)
    
    try:
        # ユーザーを削除すると、CASCADEで関連システムも削除される
        test_user.delete()
        print("✅ テストデータを削除しました")
    except Exception as e:
        print(f"⚠️ クリーンアップエラー: {e}")
    
    print("\n" + "=" * 60)
    print("テスト完了")
    print("=" * 60)

if __name__ == "__main__":
    test_tutorial_systems_creation()
