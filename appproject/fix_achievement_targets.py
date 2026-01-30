import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from codemon.models import Achievement

# target_count修正マッピング
achievement_settings = {
    # システム作成実績
    '初めてのシステム': {'target': 1, 'tier': 'bronze', 'coins': 100},
    'システム初心者卒業': {'target': 5, 'tier': 'silver', 'coins': 300},
    'システムベテラン': {'target': 10, 'tier': 'gold', 'coins': 500},
    'システムマスター': {'target': 25, 'tier': 'diamond', 'coins': 1000},
    'システムレジェンド': {'target': 50, 'tier': 'platinum', 'coins': 2000},
    
    # アルゴリズム作成実績
    '初めてのアルゴリズム': {'target': 1, 'tier': 'bronze', 'coins': 100},
    'アルゴリズム初心者卒業': {'target': 5, 'tier': 'silver', 'coins': 300},
    'アルゴリズムベテラン': {'target': 10, 'tier': 'gold', 'coins': 500},
    'アルゴリズムマスター': {'target': 25, 'tier': 'diamond', 'coins': 1000},
    'アルゴリズムレジェンド': {'target': 50, 'tier': 'platinum', 'coins': 2000},
    
    # ログイン実績
    '初ログイン': {'target': 1, 'tier': 'bronze', 'coins': 50},
    '1週間の友': {'target': 7, 'tier': 'silver', 'coins': 200},
    '1ヶ月の友': {'target': 30, 'tier': 'gold', 'coins': 500},
    '100日の友': {'target': 100, 'tier': 'diamond', 'coins': 1000},
    '年の友': {'target': 365, 'tier': 'platinum', 'coins': 3000},
    
    # 連続ログイン実績
    '3日連続': {'target': 3, 'tier': 'bronze', 'coins': 100},
    '1週間連続': {'target': 7, 'tier': 'silver', 'coins': 300},
    '1ヶ月連続': {'target': 30, 'tier': 'gold', 'coins': 1000},
    
    # AI会話実績
    '初めての会話': {'target': 1, 'tier': 'bronze', 'coins': 50},
    'おしゃべり好き': {'target': 10, 'tier': 'silver', 'coins': 200},
    '会話マスター': {'target': 50, 'tier': 'gold', 'coins': 500},
}

print("実績の目標値、ティア、報酬を修正中...")
updated_count = 0

for name, settings in achievement_settings.items():
    try:
        achievement = Achievement.objects.get(name=name)
        updated = False
        
        if achievement.target_count != settings['target']:
            print(f"修正: {name} - target_count: {achievement.target_count} -> {settings['target']}")
            achievement.target_count = settings['target']
            updated = True
        
        if achievement.tier != settings['tier']:
            print(f"修正: {name} - tier: {achievement.tier} -> {settings['tier']}")
            achievement.tier = settings['tier']
            updated = True
        
        if achievement.reward_coins != settings['coins']:
            print(f"修正: {name} - reward_coins: {achievement.reward_coins} -> {settings['coins']}")
            achievement.reward_coins = settings['coins']
            updated = True
        
        if updated:
            achievement.save()
            updated_count += 1
        else:
            print(f"OK: {name}")
            
    except Achievement.DoesNotExist:
        print(f"警告: 実績 '{name}' が見つかりません")

print(f"\n合計 {updated_count} 件の実績を修正しました")

# 確認
print("\n=== 修正後の実績一覧 ===")
for category in ['system', 'algorithm', 'login', 'consecutive_login', 'ai_chat']:
    achs = Achievement.objects.filter(category=category).order_by('target_count')
    if achs.exists():
        print(f"\n[{category}]:")
        for a in achs:
            print(f"  {a.name}: target={a.target_count}, tier={a.tier}, coins={a.reward_coins}")
