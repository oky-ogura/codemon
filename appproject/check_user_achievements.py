"""
ユーザーの実績状況を確認
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from codemon.models import UserStats, UserAchievement, Achievement
from accounts.models import Account

user = Account.objects.first()
if not user:
    print("ユーザーが見つかりません")
else:
    print(f"ユーザー: {user.user_name}")
    
    stats, _ = UserStats.objects.get_or_create(user=user)
    print(f"総システム数: {stats.total_systems}")
    
    print(f"\nシステムカテゴリの全実績:")
    for ach in Achievement.objects.filter(category='system').order_by('target_count'):
        print(f"  {ach.name} - target: {ach.target_count}, tier: {ach.tier}")
        ua = UserAchievement.objects.filter(user=user, achievement=ach).first()
        if ua:
            print(f"    -> current: {ua.current_count}, achieved: {ua.is_achieved}")
        else:
            print(f"    -> UserAchievementなし")
    
    print(f"\n達成済みシステム実績（最高ティア）:")
    system_achievements = UserAchievement.objects.filter(
        user=user,
        achievement__category='system',
        is_achieved=True
    ).select_related('achievement').order_by('-achievement__target_count')
    
    if system_achievements.exists():
        highest = system_achievements.first()
        print(f"  {highest.achievement.name} (target: {highest.achievement.target_count})")
    else:
        print("  達成済み実績なし → デフォルト: システムビギナー")
