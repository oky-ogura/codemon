"""
テンプレートコピー機能のテスト
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
from django.conf import settings

def test_template_copy():
    print("=" * 60)
    print("テンプレートコピー機能テスト")
    print("=" * 60)
    
    # 1. テンプレートユーザーの確認
    template_user_id = getattr(settings, 'TUTORIAL_TEMPLATE_USER_ID', None)
    print(f"\n📋 テンプレートユーザーID: {template_user_id}")
    
    if not template_user_id:
        print("❌ TUTORIAL_TEMPLATE_USER_IDが設定されていません")
        return
    
    try:
        template_user = Account.objects.get(user_id=template_user_id)
        print(f"✅ テンプレートユーザー: {template_user.user_name}")
    except Account.DoesNotExist:
        print(f"❌ user_id={template_user_id} のユーザーが見つかりません")
        return
    
    # 2. テンプレートシステムの確認
    print("\n📋 テンプレートシステムの確認:")
    template_correct = System.objects.filter(user=template_user, system_name="正解").first()
    template_incorrect = System.objects.filter(user=template_user, system_name="不正解").first()
    
    if template_correct:
        elem_count = SystemElement.objects.filter(system=template_correct).count()
        print(f"  ✅ 「正解」システム: ID={template_correct.system_id}, 要素数={elem_count}")
        
        # 要素の詳細を表示
        for elem in SystemElement.objects.filter(system=template_correct):
            print(f"      - {elem.element_type}: {elem.element_label} at ({elem.position_x}, {elem.position_y})")
    else:
        print("  ❌ 「正解」システムが見つかりません")
    
    if template_incorrect:
        elem_count = SystemElement.objects.filter(system=template_incorrect).count()
        print(f"  ✅ 「不正解」システム: ID={template_incorrect.system_id}, 要素数={elem_count}")
        
        # 要素の詳細を表示
        for elem in SystemElement.objects.filter(system=template_incorrect):
            print(f"      - {elem.element_type}: {elem.element_label} at ({elem.position_x}, {elem.position_y})")
    else:
        print("  ❌ 「不正解」システムが見つかりません")
    
    # 3. テストユーザーの作成
    print("\n📋 テストユーザーの作成:")
    test_username = f"test_copy_user_{Account.objects.count() + 1}"
    
    try:
        from django.contrib.auth.hashers import make_password
        
        test_user = Account.objects.create(
            user_name=test_username,
            email=f"{test_username}@example.com",
            password=make_password("testpass123"),
            account_type="teacher"
        )
        print(f"  ✅ テストユーザー作成: {test_user.user_name} (ID={test_user.user_id})")
        
        # 4. チュートリアルシステムの作成（コピー）
        print("\n📋 チュートリアルシステムのコピー:")
        correct_sys, incorrect_sys = create_tutorial_systems(test_user)
        
        if correct_sys:
            elem_count = SystemElement.objects.filter(system=correct_sys).count()
            print(f"  ✅ 正解システムコピー: ID={correct_sys.system_id}, 要素数={elem_count}")
            
            # コピーされた要素を確認
            for elem in SystemElement.objects.filter(system=correct_sys):
                print(f"      - {elem.element_type}: {elem.element_label} at ({elem.position_x}, {elem.position_y})")
        else:
            print("  ❌ 正解システムのコピーに失敗")
        
        if incorrect_sys:
            elem_count = SystemElement.objects.filter(system=incorrect_sys).count()
            print(f"  ✅ 不正解システムコピー: ID={incorrect_sys.system_id}, 要素数={elem_count}")
            
            # コピーされた要素を確認
            for elem in SystemElement.objects.filter(system=incorrect_sys):
                print(f"      - {elem.element_type}: {elem.element_label} at ({elem.position_x}, {elem.position_y})")
        else:
            print("  ❌ 不正解システムのコピーに失敗")
        
        # 5. コピー内容の検証
        print("\n📋 コピー内容の検証:")
        if template_correct and correct_sys:
            template_elems = SystemElement.objects.filter(system=template_correct).count()
            copied_elems = SystemElement.objects.filter(system=correct_sys).count()
            
            if template_elems == copied_elems:
                print(f"  ✅ 正解システムの要素数一致: {copied_elems}個")
            else:
                print(f"  ❌ 要素数が一致しません: テンプレート={template_elems}, コピー={copied_elems}")
        
        if template_incorrect and incorrect_sys:
            template_elems = SystemElement.objects.filter(system=template_incorrect).count()
            copied_elems = SystemElement.objects.filter(system=incorrect_sys).count()
            
            if template_elems == copied_elems:
                print(f"  ✅ 不正解システムの要素数一致: {copied_elems}個")
            else:
                print(f"  ❌ 要素数が一致しません: テンプレート={template_elems}, コピー={copied_elems}")
        
        # 6. クリーンアップ
        print("\n📋 テストデータのクリーンアップ:")
        test_user.delete()
        print(f"  ✅ テストユーザー削除: {test_username}")
        
    except Exception as e:
        print(f"\n❌ エラー発生: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("テスト完了")
    print("=" * 60)

if __name__ == "__main__":
    test_template_copy()
