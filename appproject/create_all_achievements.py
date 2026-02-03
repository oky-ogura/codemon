"""
全実績データを作成するスクリプト（コンセプト準拠版）
Usage: python create_all_achievements.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from codemon.models import Achievement
from django.db import transaction


def create_all_achievements():
    """全実績マスターデータを作成（コンセプト通り）"""
    
    achievements = [
        # ===== ログイン実績（累計） =====
        {
            'category': 'login',
            'tier': 'bronze',
            'name': '初ログイン',
            'description': '初回ログイン',
            'target_count': 1,
            'reward_coins': 100,
            'icon': '👋',
            'display_order': 10
        },
        {
            'category': 'login',
            'tier': 'silver',
            'name': '3日の友',
            'description': '累計3日ログイン',
            'target_count': 3,
            'reward_coins': 200,
            'icon': '📅',
            'display_order': 11
        },
        {
            'category': 'login',
            'tier': 'gold',
            'name': '10日の友',
            'description': '累計10日ログイン',
            'target_count': 10,
            'reward_coins': 300,
            'icon': '📅',
            'display_order': 12
        },
        {
            'category': 'login',
            'tier': 'platinum',
            'name': '1ヶ月の友',
            'description': '累計30日ログイン',
            'target_count': 30,
            'reward_coins': 500,
            'icon': '📅',
            'display_order': 13
        },
        {
            'category': 'login',
            'tier': 'diamond',
            'name': '2ヶ月の友',
            'description': '累計60日ログイン',
            'target_count': 60,
            'reward_coins': 1000,
            'icon': '📅',
            'display_order': 14
        },
        
        # ===== 連続ログイン実績 =====
        {
            'category': 'consecutive_login',
            'tier': 'bronze',
            'name': '2日連続',
            'description': '2日連続ログイン',
            'target_count': 2,
            'reward_coins': 100,
            'icon': '🔥',
            'display_order': 20
        },
        {
            'category': 'consecutive_login',
            'tier': 'silver',
            'name': '5日連続',
            'description': '5日連続ログイン',
            'target_count': 5,
            'reward_coins': 200,
            'icon': '🔥',
            'display_order': 21
        },
        {
            'category': 'consecutive_login',
            'tier': 'gold',
            'name': '1週間連続',
            'description': '7日連続ログイン',
            'target_count': 7,
            'reward_coins': 300,
            'icon': '🔥',
            'display_order': 22
        },
        {
            'category': 'consecutive_login',
            'tier': 'platinum',
            'name': '2週間連続',
            'description': '14日連続ログイン',
            'target_count': 14,
            'reward_coins': 500,
            'icon': '🔥',
            'display_order': 23
        },
        {
            'category': 'consecutive_login',
            'tier': 'diamond',
            'name': '1ヶ月連続',
            'description': '30日連続ログイン',
            'target_count': 30,
            'reward_coins': 1000,
            'icon': '🔥',
            'display_order': 24
        },
        
        # ===== システム作成実績 =====
        {
            'category': 'system',
            'tier': 'bronze',
            'name': 'システムビギナー',
            'description': '1システム作成',
            'target_count': 1,
            'reward_coins': 100,
            'icon': '⚙️',
            'display_order': 30
        },
        {
            'category': 'system',
            'tier': 'silver',
            'name': 'システム職人',
            'description': '5システム作成',
            'target_count': 5,
            'reward_coins': 200,
            'icon': '⚙️',
            'display_order': 31
        },
        {
            'category': 'system',
            'tier': 'gold',
            'name': 'システムマスター',
            'description': '20システム作成',
            'target_count': 20,
            'reward_coins': 300,
            'icon': '⚙️',
            'display_order': 32
        },
        {
            'category': 'system',
            'tier': 'platinum',
            'name': 'システムエキスパート',
            'description': '50システム作成',
            'target_count': 50,
            'reward_coins': 500,
            'icon': '⚙️',
            'display_order': 33
        },
        {
            'category': 'system',
            'tier': 'diamond',
            'name': 'システムレジェンド',
            'description': '100システム作成',
            'target_count': 100,
            'reward_coins': 1000,
            'icon': '⚙️',
            'display_order': 34
        },
        
        # ===== アルゴリズム作成実績 =====
        {
            'category': 'algorithm',
            'tier': 'bronze',
            'name': 'アルゴリズムビギナー',
            'description': '1件作成',
            'target_count': 1,
            'reward_coins': 100,
            'icon': '🧩',
            'display_order': 40
        },
        {
            'category': 'algorithm',
            'tier': 'silver',
            'name': 'アルゴリズム職人',
            'description': '5件作成',
            'target_count': 5,
            'reward_coins': 200,
            'icon': '🧩',
            'display_order': 41
        },
        {
            'category': 'algorithm',
            'tier': 'gold',
            'name': 'アルゴリズムマスター',
            'description': '10件作成',
            'target_count': 10,
            'reward_coins': 300,
            'icon': '🧩',
            'display_order': 42
        },
        {
            'category': 'algorithm',
            'tier': 'platinum',
            'name': 'アルゴリズムエキスパート',
            'description': '20件作成',
            'target_count': 20,
            'reward_coins': 500,
            'icon': '🧩',
            'display_order': 43
        },
        {
            'category': 'algorithm',
            'tier': 'diamond',
            'name': 'アルゴリズムレジェンド',
            'description': '50件作成',
            'target_count': 50,
            'reward_coins': 1000,
            'icon': '🧩',
            'display_order': 44
        },
        
        # ===== AI会話実績（累計） =====
        {
            'category': 'ai_chat',
            'tier': 'bronze',
            'name': 'AI会話デビュー',
            'description': '10回会話',
            'target_count': 10,
            'reward_coins': 100,
            'icon': '💬',
            'display_order': 45
        },
        {
            'category': 'ai_chat',
            'tier': 'silver',
            'name': 'AIフレンド',
            'description': '50回会話',
            'target_count': 50,
            'reward_coins': 200,
            'icon': '💬',
            'display_order': 46
        },
        {
            'category': 'ai_chat',
            'tier': 'gold',
            'name': 'AI会話マスター',
            'description': '100回会話',
            'target_count': 100,
            'reward_coins': 300,
            'icon': '💬',
            'display_order': 47
        },
        {
            'category': 'ai_chat',
            'tier': 'platinum',
            'name': 'AI会話エキスパート',
            'description': '300回会話',
            'target_count': 300,
            'reward_coins': 500,
            'icon': '💬',
            'display_order': 48
        },
        {
            'category': 'ai_chat',
            'tier': 'diamond',
            'name': 'AI会話ベストフレンド',
            'description': '1000回会話',
            'target_count': 1000,
            'reward_coins': 1000,
            'icon': '💬',
            'display_order': 49
        },
        
        # ===== AI連続会話実績 =====
        {
            'category': 'ai_chat_consecutive',
            'tier': 'bronze',
            'name': 'AI会話ビギナー',
            'description': '2日連続でAIと会話する',
            'target_count': 2,
            'reward_coins': 100,
            'icon': '🤝',
            'display_order': 50
        },
        {
            'category': 'ai_chat_consecutive',
            'tier': 'silver',
            'name': 'AI会話パートナー',
            'description': '5日連続でAIと会話する',
            'target_count': 5,
            'reward_coins': 200,
            'icon': '🤝',
            'display_order': 51
        },
        {
            'category': 'ai_chat_consecutive',
            'tier': 'gold',
            'name': 'AI会話エンスージアスト',
            'description': '7日連続でAIと会話する',
            'target_count': 7,
            'reward_coins': 300,
            'icon': '🤝',
            'display_order': 52
        },
        {
            'category': 'ai_chat_consecutive',
            'tier': 'platinum',
            'name': 'AI会話マニア',
            'description': '14日連続でAIと会話する',
            'target_count': 14,
            'reward_coins': 500,
            'icon': '🤝',
            'display_order': 53
        },
        {
            'category': 'ai_chat_consecutive',
            'tier': 'diamond',
            'name': 'AI会話レジェンド',
            'description': '30日連続でAIと会話する',
            'target_count': 30,
            'reward_coins': 1000,
            'icon': '🤝',
            'display_order': 54
        },
        
        # ===== チェックリスト作成実績 =====
        {
            'category': 'checklist_create',
            'tier': 'bronze',
            'name': 'チェックリスト入門',
            'description': 'チェックリストを1件作成する',
            'target_count': 1,
            'reward_coins': 100,
            'icon': '📝',
            'display_order': 60
        },
        {
            'category': 'checklist_create',
            'tier': 'silver',
            'name': 'チェックリスト職人',
            'description': 'チェックリストを5件作成する',
            'target_count': 5,
            'reward_coins': 200,
            'icon': '📝',
            'display_order': 61
        },
        {
            'category': 'checklist_create',
            'tier': 'gold',
            'name': 'チェックリストマスター',
            'description': 'チェックリストを10件作成する',
            'target_count': 10,
            'reward_coins': 300,
            'icon': '📝',
            'display_order': 62
        },
        {
            'category': 'checklist_create',
            'tier': 'platinum',
            'name': 'チェックリストエキスパート',
            'description': 'チェックリストを20件作成する',
            'target_count': 20,
            'reward_coins': 500,
            'icon': '📝',
            'display_order': 63
        },
        {
            'category': 'checklist_create',
            'tier': 'diamond',
            'name': 'チェックリストレジェンド',
            'description': 'チェックリストを50件作成する',
            'target_count': 50,
            'reward_coins': 1000,
            'icon': '📝',
            'display_order': 64
        },
        
        # ===== チェックリスト完了実績 =====
        {
            'category': 'checklist_complete',
            'tier': 'bronze',
            'name': 'タスクハンター',
            'description': 'チェック項目を10個完了する',
            'target_count': 10,
            'reward_coins': 100,
            'icon': '✅',
            'display_order': 70
        },
        {
            'category': 'checklist_complete',
            'tier': 'silver',
            'name': 'タスクマスター',
            'description': 'チェック項目を50個完了する',
            'target_count': 50,
            'reward_coins': 200,
            'icon': '✅',
            'display_order': 71
        },
        {
            'category': 'checklist_complete',
            'tier': 'gold',
            'name': 'タスクチャンピオン',
            'description': 'チェック項目を100個完了する',
            'target_count': 100,
            'reward_coins': 300,
            'icon': '✅',
            'display_order': 72
        },
        {
            'category': 'checklist_complete',
            'tier': 'platinum',
            'name': 'タスククラッシャー',
            'description': 'チェック項目を300個完了する',
            'target_count': 300,
            'reward_coins': 500,
            'icon': '✅',
            'display_order': 73
        },
        {
            'category': 'checklist_complete',
            'tier': 'diamond',
            'name': 'タスクアルティメット',
            'description': 'チェック項目を1000個完了する',
            'target_count': 1000,
            'reward_coins': 1000,
            'icon': '✅',
            'display_order': 74
        },
        
        # ===== アクセサリー購入実績 =====
        {
            'category': 'accessory',
            'tier': 'bronze',
            'name': 'おしゃれ初心者',
            'description': '初めてアクセサリーを購入する',
            'target_count': 1,
            'reward_coins': 100,
            'icon': '🎀',
            'display_order': 80
        },
        {
            'category': 'accessory',
            'tier': 'silver',
            'name': 'ファッションハンター',
            'description': 'アクセサリーを3個購入する',
            'target_count': 3,
            'reward_coins': 200,
            'icon': '🎀',
            'display_order': 81
        },
        {
            'category': 'accessory',
            'tier': 'gold',
            'name': 'スタイリスト',
            'description': 'アクセサリーを5個購入する',
            'target_count': 5,
            'reward_coins': 300,
            'icon': '🎀',
            'display_order': 82
        },
        {
            'category': 'accessory',
            'tier': 'platinum',
            'name': 'ファッショニスタ',
            'description': 'アクセサリーを10個購入する',
            'target_count': 10,
            'reward_coins': 500,
            'icon': '🎀',
            'display_order': 83
        },
        {
            'category': 'accessory',
            'tier': 'diamond',
            'name': 'コレクター',
            'description': 'アクセサリーを20個購入する',
            'target_count': 20,
            'reward_coins': 1000,
            'icon': '🎀',
            'display_order': 84
        },
    ]
    
    created_count = 0
    updated_count = 0
    
    with transaction.atomic():
        for ach_data in achievements:
            achievement, created = Achievement.objects.update_or_create(
                category=ach_data['category'],
                tier=ach_data['tier'],
                defaults=ach_data
            )
            
            if created:
                created_count += 1
                print(f"✅ 作成: {achievement.name} ({achievement.get_category_display()} - {achievement.get_tier_display()})")
            else:
                updated_count += 1
                print(f"🔄 更新: {achievement.name} ({achievement.get_category_display()} - {achievement.get_tier_display()})")
    
    print(f"\n✨ 完了: {created_count}件作成, {updated_count}件更新")
    print(f"📊 全実績数: {Achievement.objects.count()}件")
    
    # カテゴリ別集計
    print("\n📋 カテゴリ別実績数:")
    from django.db.models import Count
    categories = Achievement.objects.values('category').annotate(count=Count('category')).order_by('category')
    for cat in categories:
        category_display = dict(Achievement.CATEGORY_CHOICES).get(cat['category'], cat['category'])
        print(f"  - {category_display}: {cat['count']}件")


if __name__ == '__main__':
    print("🚀 全実績データを作成します（コンセプト準拠版）...\n")
    create_all_achievements()
