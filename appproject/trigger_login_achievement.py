"""
ログイン実績を強制的にトリガーするスクリプト
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from accounts.models import Account
from codemon.achievement_utils import update_login_stats
from codemon.models import UserAchievement, Achievement

# ユーザーを取得
user = Account.objects.first()

if user:
    print(f"ユーザー: {user.user_name} ({user.user_id})")
    
    # ログイン統計を強制更新
    print("\nログイン統計を更新中...")
    newly_achieved = update_login_stats(user)
    
    print(f"新規達成実績: {len(newly_achieved)}件")
    for achievement in newly_achieved:
        print(f"  - {achievement.name}: {achievement.reward_coins}コイン")
    
    # 達成済み実績を確認
    print("\n【達成済み実績の確認】")
    achieved = UserAchievement.objects.filter(
        user=user,
        is_achieved=True
    ).select_related('achievement')
    
    print(f"総数: {achieved.count()}件")
    
    for ua in achieved:
        rewarded_status = "✅ 受取済み" if ua.is_rewarded else "⏳ 未受取"
        print(f"  {rewarded_status} - {ua.achievement.name}: {ua.achievement.reward_coins}コイン")
else:
    print("ユーザーが見つかりません")
