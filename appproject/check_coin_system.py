"""
コイン獲得システムの診断スクリプト
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from accounts.models import Account
from codemon.models import UserCoin, UserAchievement, Achievement

def check_coin_system():
    print("=" * 60)
    print("コインシステム診断")
    print("=" * 60)
    
    # テストユーザーを取得（最初のユーザー）
    test_user = Account.objects.first()
    
    if not test_user:
        print("❌ ユーザーが見つかりません")
        return
    
    print(f"\n✅ ユーザー: {test_user.user_name} ({test_user.user_id})")
    
    # UserCoinレコードを確認
    try:
        user_coin = UserCoin.objects.get(user=test_user)
        print(f"\n【UserCoinレコード】")
        print(f"  現在残高: {user_coin.balance} コイン")
        print(f"  累計獲得: {user_coin.total_earned} コイン")
    except UserCoin.DoesNotExist:
        print("\n❌ UserCoinレコードが存在しません")
        user_coin = None
    
    # 達成済み実績を確認
    achieved = UserAchievement.objects.filter(
        user=test_user,
        is_achieved=True
    ).select_related('achievement')
    
    print(f"\n【達成済み実績】")
    print(f"  総数: {achieved.count()}件")
    
    rewarded_count = achieved.filter(is_rewarded=True).count()
    unrewarded_count = achieved.filter(is_rewarded=False).count()
    
    print(f"  報酬受取済み: {rewarded_count}件")
    print(f"  報酬未受取: {unrewarded_count}件")
    
    # 未受取実績の詳細
    if unrewarded_count > 0:
        print(f"\n【未受取実績の詳細】")
        unrewarded = achieved.filter(is_rewarded=False)
        total_unrewarded_coins = 0
        for ua in unrewarded:
            print(f"  - {ua.achievement.name}: {ua.achievement.reward_coins}コイン")
            total_unrewarded_coins += ua.achievement.reward_coins
        print(f"  未受取総額: {total_unrewarded_coins}コイン")
    
    # 受取済み実績の詳細
    if rewarded_count > 0:
        print(f"\n【受取済み実績の詳細】")
        rewarded = achieved.filter(is_rewarded=True)
        total_rewarded_coins = 0
        for ua in rewarded:
            print(f"  - {ua.achievement.name}: {ua.achievement.reward_coins}コイン (受取日時: {ua.rewarded_at})")
            total_rewarded_coins += ua.achievement.reward_coins
        print(f"  受取済み総額: {total_rewarded_coins}コイン")
        
        # 整合性チェック
        if user_coin and user_coin.total_earned != total_rewarded_coins:
            print(f"\n⚠️  警告: UserCoin.total_earned ({user_coin.total_earned}) と受取済み実績の合計 ({total_rewarded_coins}) が一致しません")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    check_coin_system()
