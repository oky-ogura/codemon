"""
古い実績「初めてのシステム」を削除し、ユーザー実績を更新
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from codemon.models import UserStats, Achievement
from codemon.achievement_utils import check_and_grant_achievements
from accounts.models import Account

# 古い実績を削除
old_achievement = Achievement.objects.filter(name='初めてのシステム').first()
if old_achievement:
    print(f"古い実績を削除: {old_achievement.name}")
    old_achievement.delete()
else:
    print("古い実績は既に削除されています")

# 全ユーザーのシステム実績をチェック
users = Account.objects.all()
for user in users:
    stats, _ = UserStats.objects.get_or_create(user=user)
    if stats.total_systems > 0:
        print(f"\n{user.user_name} のシステム実績をチェック (システム数: {stats.total_systems})")
        newly_achieved = check_and_grant_achievements(user, 'system', stats.total_systems)
        if newly_achieved:
            for ach in newly_achieved:
                print(f"  ✅ 達成: {ach.name}")
        else:
            print("  新規達成実績なし")

print("\n完了！")
