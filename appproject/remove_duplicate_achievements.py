"""
重複実績を削除するスクリプト
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from codemon.models import Achievement, UserAchievement

print("=" * 60)
print("重複実績の削除")
print("=" * 60)

# 重複している「初ログイン」実績を特定
login_achievements = Achievement.objects.filter(
    name="初ログイン",
    category="login",
    target_count=1
).order_by('achievement_id')

print(f"\n「初ログイン」実績の数: {login_achievements.count()}件")

if login_achievements.count() > 1:
    # 最初の実績を残し、後のものを削除
    keep = login_achievements.first()
    duplicates = login_achievements.exclude(achievement_id=keep.achievement_id)
    
    print(f"\n保持: {keep.achievement_id} - {keep.name}")
    print(f"削除対象:")
    
    for dup in duplicates:
        # 関連するUserAchievementを削除
        user_achievements = UserAchievement.objects.filter(achievement=dup)
        print(f"  {dup.achievement_id} - {dup.name} (関連UserAchievement: {user_achievements.count()}件)")
        user_achievements.delete()
        dup.delete()
    
    print("\n✅ 重複実績を削除しました")
else:
    print("\n✅ 重複はありません")

print("=" * 60)
