import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from codemon.models import Achievement

# カテゴリー修正マッピング
category_mapping = {
    # アルゴリズム実績
    '初めてのアルゴリズム': 'algorithm',
    'アルゴリズム初心者卒業': 'algorithm',
    'アルゴリズムベテラン': 'algorithm',
    'アルゴリズムマスター': 'algorithm',
    'アルゴリズムレジェンド': 'algorithm',
    
    # ログイン実績
    '初ログイン': 'login',
    '1週間の友': 'login',
    '1ヶ月の友': 'login',
    '100日の友': 'login',
    '年の友': 'login',
    
    # 連続ログイン実績
    '3日連続': 'consecutive_login',
    '1週間連続': 'consecutive_login',
    '1ヶ月連続': 'consecutive_login',
    
    # AI会話実績
    '初めての会話': 'ai_chat',
    'おしゃべり好き': 'ai_chat',
    '会話マスター': 'ai_chat',
}

print("実績カテゴリーを修正中...")
updated_count = 0

for name, correct_category in category_mapping.items():
    try:
        achievement = Achievement.objects.get(name=name)
        if achievement.category != correct_category:
            print(f"修正: {name} ({achievement.category} -> {correct_category})")
            achievement.category = correct_category
            achievement.save()
            updated_count += 1
        else:
            print(f"OK: {name} ({correct_category})")
    except Achievement.DoesNotExist:
        print(f"警告: 実績 '{name}' が見つかりません")

print(f"\n合計 {updated_count} 件の実績を修正しました")

# 確認
print("\n=== 修正後のカテゴリー別集計 ===")
for category in ['system', 'algorithm', 'login', 'consecutive_login', 'ai_chat']:
    count = Achievement.objects.filter(category=category).count()
    print(f"{category}: {count}件")
