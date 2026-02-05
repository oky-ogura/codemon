"""
実績データを初期化するスクリプト
Usage: python initialize_achievements.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from codemon.models import Achievement, UserStats
from accounts.models import Account
from django.db import transaction


def create_achievements():
    """実績マスターデータを作成"""
    achievements = [
        # システム作成系
        {
            'name': '初めてのシステム',
            'description': '初めてシステムを作成した！',
            'category': 'system',
            'tier': None,
            'target_count': 1,
            'reward_coins': 100,
            'icon': '🎉',
            'display_order': 1
        },
        {
            'name': 'システム初心者卒業',
            'description': 'システムを10個作成した',
            'category': 'system',
            'tier': 'bronze',
            'target_count': 10,
            'reward_coins': 100,
            'icon': '🥉',
            'display_order': 2
        },
        {
            'name': 'システムベテラン',
            'description': 'システムを50個作成した',
            'category': 'system',
            'tier': 'silver',
            'target_count': 50,
            'reward_coins': 200,
            'icon': '🥈',
            'display_order': 3
        },
        {
            'name': 'システムマスター',
            'description': 'システムを100個作成した',
            'category': 'system',
            'tier': 'gold',
            'target_count': 100,
            'reward_coins': 300,
            'icon': '🥇',
            'display_order': 4
        },
        {
            'name': 'システムレジェンド',
            'description': 'システムを200個作成した',
            'category': 'system',
            'tier': 'platinum',
            'target_count': 200,
            'reward_coins': 1000,
            'icon': '👑',
            'display_order': 5
        },
        
        # アルゴリズム作成系
        {
            'name': '初めてのアルゴリズム',
            'description': '初めてアルゴリズムを作成した！',
            'category': 'algorithm',
            'tier': None,
            'target_count': 1,
            'reward_coins': 100,
            'icon': '🎉',
            'display_order': 11
        },
        {
            'name': 'アルゴリズム初心者卒業',
            'description': 'アルゴリズムを10個作成した',
            'category': 'algorithm',
            'tier': 'bronze',
            'target_count': 10,
            'reward_coins': 100,
            'icon': '🥉',
            'display_order': 12
        },
        {
            'name': 'アルゴリズムベテラン',
            'description': 'アルゴリズムを50個作成した',
            'category': 'algorithm',
            'tier': 'silver',
            'target_count': 50,
            'reward_coins': 200,
            'icon': '🥈',
            'display_order': 13
        },
        {
            'name': 'アルゴリズムマスター',
            'description': 'アルゴリズムを100個作成した',
            'category': 'algorithm',
            'tier': 'gold',
            'target_count': 100,
            'reward_coins': 300,
            'icon': '🥇',
            'display_order': 14
        },
        {
            'name': 'アルゴリズムレジェンド',
            'description': 'アルゴリズムを200個作成した',
            'category': 'algorithm',
            'tier': 'platinum',
            'target_count': 200,
            'reward_coins': 1000,
            'icon': '👑',
            'display_order': 15
        },
        
        # ログイン系
        {
            'name': '初ログイン',
            'description': 'プログラミング学習の第一歩！',
            'category': 'login',
            'tier': None,
            'target_count': 1,
            'reward_coins': 100,
            'icon': '👋',
            'display_order': 21
        },
        {
            'name': '1週間の友',
            'description': '7日間ログインした',
            'category': 'login',
            'tier': 'bronze',
            'target_count': 7,
            'reward_coins': 200,
            'icon': '🥉',
            'display_order': 22
        },
        {
            'name': '1ヶ月の友',
            'description': '30日間ログインした',
            'category': 'login',
            'tier': 'silver',
            'target_count': 30,
            'reward_coins': 300,
            'icon': '🥈',
            'display_order': 23
        },
        {
            'name': '100日の友',
            'description': '100日間ログインした',
            'category': 'login',
            'tier': 'gold',
            'target_count': 100,
            'reward_coins': 500,
            'icon': '🥇',
            'display_order': 24
        },
        {
            'name': '年の友',
            'description': '365日間ログインした',
            'category': 'login',
            'tier': 'platinum',
            'target_count': 365,
            'reward_coins': 1000,
            'icon': '🎊',
            'display_order': 25
        },
        
        # 連続ログイン系
        {
            'name': '3日連続',
            'description': '3日連続でログインした',
            'category': 'consecutive_login',
            'tier': 'bronze',
            'target_count': 3,
            'reward_coins': 200,
            'icon': '🔥',
            'display_order': 31
        },
        {
            'name': '1週間連続',
            'description': '7日連続でログインした',
            'category': 'consecutive_login',
            'tier': 'silver',
            'target_count': 7,
            'reward_coins': 300,
            'icon': '🔥',
            'display_order': 32
        },
        {
            'name': '1ヶ月連続',
            'description': '30日連続でログインした',
            'category': 'consecutive_login',
            'tier': 'gold',
            'target_count': 30,
            'reward_coins': 1000,
            'icon': '🔥',
            'display_order': 33
        },
        
        # AI会話系
        {
            'name': '初めての会話',
            'description': '相棒AIと初めて会話した！',
            'category': 'ai_chat',
            'tier': None,
            'target_count': 1,
            'reward_coins': 100,
            'icon': '💬',
            'display_order': 41
        },
        {
            'name': 'おしゃべり好き',
            'description': '相棒AIと10回会話した',
            'category': 'ai_chat',
            'tier': 'bronze',
            'target_count': 10,
            'reward_coins': 200,
            'icon': '💬',
            'display_order': 42
        },
        {
            'name': '会話マスター',
            'description': '相棒AIと50回会話した',
            'category': 'ai_chat',
            'tier': 'silver',
            'target_count': 50,
            'reward_coins': 500,
            'icon': '💬',
            'display_order': 43
        },
    ]
    
    created_count = 0
    with transaction.atomic():
        for ach_data in achievements:
            achievement, created = Achievement.objects.get_or_create(
                name=ach_data['name'],
                defaults=ach_data
            )
            if created:
                created_count += 1
                print(f"✓ 作成: {achievement.name}")
            else:
                print(f"  既存: {achievement.name}")
    
    print(f"\n実績データ: {created_count}件作成, {len(achievements) - created_count}件既存")


def initialize_user_stats():
    """既存ユーザーのUserStatsを作成し、既存データをカウント"""
    users = Account.objects.all()
    created_count = 0
    updated_count = 0
    
    with transaction.atomic():
        for user in users:
            stats, created = UserStats.objects.get_or_create(user=user)
            
            if created or stats.total_systems == 0:
                # システム作成数をカウント
                from codemon.models import System, Algorithm
                stats.total_systems = System.objects.filter(user=user).count()
                stats.total_algorithms = Algorithm.objects.filter(user=user).count()
                
                # AI会話数をカウント
                from codemon.models import AIConversation
                stats.total_ai_chats = AIConversation.objects.filter(user=user).count()
                
                stats.save()
                
                if created:
                    created_count += 1
                    print(f"✓ 作成: {user.user_name} (システム:{stats.total_systems}, アルゴリズム:{stats.total_algorithms}, AI会話:{stats.total_ai_chats})")
                else:
                    updated_count += 1
                    print(f"  更新: {user.user_name} (システム:{stats.total_systems}, アルゴリズム:{stats.total_algorithms}, AI会話:{stats.total_ai_chats})")
    
    print(f"\nユーザー統計: {created_count}件作成, {updated_count}件更新")


if __name__ == '__main__':
    print("=" * 60)
    print("実績システム初期化")
    print("=" * 60)
    
    print("\n[1] 実績マスターデータ作成")
    create_achievements()
    
    print("\n[2] ユーザー統計初期化")
    initialize_user_stats()
    
    print("\n" + "=" * 60)
    print("初期化完了！")
    print("=" * 60)
