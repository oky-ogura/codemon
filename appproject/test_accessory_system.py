"""
アクセサリー機能のテストと診断
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from accounts.models import Account
from codemon.models import Accessory, UserAccessory, UserCoin


def test_accessory_system():
    """アクセサリーシステムの動作確認"""
    
    print("=" * 60)
    print("アクセサリー機能診断")
    print("=" * 60)
    
    # 1. アクセサリーデータの確認
    print("\n[1] アクセサリーデータ")
    total = Accessory.objects.count()
    with_image = Accessory.objects.filter(use_image=True).count()
    print(f"  - 総数: {total}件")
    print(f"  - 画像あり: {with_image}件")
    print(f"  - CSS描画: {total - with_image}件")
    
    # カテゴリ別
    from django.db.models import Count
    categories = Accessory.objects.values('category').annotate(count=Count('category'))
    print(f"\n  カテゴリ別:")
    for cat in categories:
        print(f"    - {cat['category']}: {cat['count']}件")
    
    # 2. テストユーザーの確認
    print("\n[2] テストユーザー")
    user = Account.objects.first()
    if user:
        print(f"  - ユーザー名: {user.user_name}")
        coin, created = UserCoin.objects.get_or_create(user=user)
        print(f"  - コイン残高: {coin.balance}コイン")
        
        # 所持アクセサリー
        owned = UserAccessory.objects.filter(user=user).count()
        equipped = UserAccessory.objects.filter(user=user, is_equipped=True).count()
        print(f"  - 所持アクセサリー: {owned}個")
        print(f"  - 装備中: {equipped}個")
    else:
        print("  ⚠️  テストユーザーが見つかりません")
    
    # 3. 購入可能なアクセサリー
    print("\n[3] 購入可能なアクセサリー（コイン解放）")
    purchasable = Accessory.objects.filter(unlock_coins__gt=0).order_by('unlock_coins')[:5]
    for acc in purchasable:
        print(f"  - {acc.name}: {acc.unlock_coins}コイン")
    
    # 4. 画像パスの確認
    print("\n[4] 画像アクセサリーのサンプル")
    image_accs = Accessory.objects.filter(use_image=True)[:5]
    for acc in image_accs:
        print(f"  - {acc.name}")
        print(f"    画像: {acc.image_path}")
        print(f"    CSSクラス: {acc.css_class}")
    
    # 5. 問題の診断
    print("\n[5] 問題診断")
    issues = []
    
    # アクセサリーが少ない
    if total < 10:
        issues.append("⚠️  アクセサリー数が少なすぎます")
    
    # 画像が設定されていない
    if with_image < 10:
        issues.append(f"⚠️  画像が設定されているのは{with_image}件のみです")
    
    # テストユーザーにコインがない
    if user and coin.balance == 0:
        issues.append("💰 テストユーザーにコインがありません（テスト用に追加推奨）")
    
    if issues:
        for issue in issues:
            print(f"  {issue}")
    else:
        print("  ✅ 問題は見つかりませんでした")
    
    print("\n" + "=" * 60)
    print("診断完了")
    print("=" * 60)


if __name__ == '__main__':
    test_accessory_system()
