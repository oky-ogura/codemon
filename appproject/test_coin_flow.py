"""
コイン獲得フローの統合テスト
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from accounts.models import Account
from codemon.models import UserCoin, UserAchievement, Achievement

print("=" * 70)
print("コイン獲得フロー - 統合テスト")
print("=" * 70)

# テストユーザーを取得
user = Account.objects.first()

if not user:
    print("❌ ユーザーが見つかりません")
    exit(1)

print(f"\n✅ テストユーザー: {user.user_name} ({user.user_id})")

# 現在のコイン残高
user_coin, _ = UserCoin.objects.get_or_create(user=user)
print(f"\n【現在のコイン残高】")
print(f"  残高: {user_coin.balance} コイン")
print(f"  累計獲得: {user_coin.total_earned} コイン")

# 達成済み実績
achieved = UserAchievement.objects.filter(
    user=user,
    is_achieved=True
).select_related('achievement')

print(f"\n【達成済み実績】")
print(f"  総数: {achieved.count()}件")

unrewarded = achieved.filter(is_rewarded=False)
rewarded = achieved.filter(is_rewarded=True)

print(f"  未受取: {unrewarded.count()}件")
if unrewarded.exists():
    total_unrewarded = sum(ua.achievement.reward_coins for ua in unrewarded)
    print(f"  ├─ 受取可能総額: {total_unrewarded}コイン")
    for ua in unrewarded:
        print(f"  └─ {ua.achievement.name}: {ua.achievement.reward_coins}コイン")

print(f"\n  受取済み: {rewarded.count()}件")
if rewarded.exists():
    total_rewarded = sum(ua.achievement.reward_coins for ua in rewarded)
    print(f"  └─ 受取済み総額: {total_rewarded}コイン")

# 整合性チェック
print(f"\n【整合性チェック】")
if rewarded.exists():
    total_rewarded = sum(ua.achievement.reward_coins for ua in rewarded)
    if user_coin.total_earned == total_rewarded:
        print(f"  ✅ OK: UserCoin.total_earned ({user_coin.total_earned}) = 受取済み実績の合計 ({total_rewarded})")
    else:
        print(f"  ⚠️  警告: UserCoin.total_earned ({user_coin.total_earned}) ≠ 受取済み実績の合計 ({total_rewarded})")
else:
    if user_coin.total_earned == 0:
        print(f"  ✅ OK: 実績未受取のため UserCoin.total_earned = 0")
    else:
        print(f"  ⚠️  警告: 実績未受取なのに UserCoin.total_earned = {user_coin.total_earned}")

# 次のアクション
print(f"\n【次のアクション】")
if unrewarded.exists():
    print(f"  🎯 トロフィーページで {unrewarded.count()} 件の実績報酬を受け取ってください")
    print(f"     URL: http://127.0.0.1:8000/codemon/achievements/")
    total_unrewarded = sum(ua.achievement.reward_coins for ua in unrewarded)
    expected_balance = user_coin.balance + total_unrewarded
    print(f"     受取後の予想残高: {user_coin.balance} + {total_unrewarded} = {expected_balance}コイン")
else:
    print(f"  ✅ 未受取の実績はありません")

print("\n" + "=" * 70)
