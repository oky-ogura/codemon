"""
不足している実績を追加するスクリプト
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from codemon.models import Achievement

def add_missing_achievements():
    """不足している実績を追加"""
    
    achievements_to_add = [
        # チェックリスト作成実績
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
        
        # チェックリスト完了実績
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
        
        # AI連続会話実績
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
        
        # アクセサリー購入実績
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
    
    for ach_data in achievements_to_add:
        achievement, created = Achievement.objects.get_or_create(
            category=ach_data['category'],
            tier=ach_data['tier'],
            defaults={
                'name': ach_data['name'],
                'description': ach_data['description'],
                'target_count': ach_data['target_count'],
                'reward_coins': ach_data['reward_coins'],
                'icon': ach_data['icon'],
                'display_order': ach_data['display_order'],
            }
        )
        
        if created:
            created_count += 1
            print(f"✅ 作成: {achievement.name} ({achievement.get_category_display()} - {achievement.get_tier_display()})")
        else:
            # 既存の場合は更新
            achievement.name = ach_data['name']
            achievement.description = ach_data['description']
            achievement.target_count = ach_data['target_count']
            achievement.reward_coins = ach_data['reward_coins']
            achievement.icon = ach_data['icon']
            achievement.display_order = ach_data['display_order']
            achievement.save()
            updated_count += 1
            print(f"🔄 更新: {achievement.name} ({achievement.get_category_display()} - {achievement.get_tier_display()})")
    
    print(f"\n✨ 完了: {created_count}件作成, {updated_count}件更新")
    print(f"📊 全実績数: {Achievement.objects.count()}件")


if __name__ == '__main__':
    print("🚀 不足している実績を追加します...\n")
    add_missing_achievements()
