"""
アクセサリーマスターデータの確認スクリプト
"""
import os
import sys
import django

# Djangoの設定を読み込む
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from codemon.models import Accessory
from django.db.models import Count

print("="*50)
print("アクセサリーマスターデータ確認")
print("="*50)

total = Accessory.objects.count()
print(f"\n✅ アクセサリー総数: {total}件\n")

if total > 0:
    # カテゴリー別集計
    print("【カテゴリー別】")
    categories = Accessory.objects.values('category').annotate(
        count=Count('category')
    ).order_by('category')
    
    for cat in categories:
        print(f"  - {cat['category']}: {cat['count']}件")
    
    # サンプル表示
    print("\n【サンプル（各カテゴリー1件ずつ）】")
    for cat in categories:
        sample = Accessory.objects.filter(category=cat['category']).first()
        if sample:
            print(f"\n  [{cat['category']}] {sample.name}")
            print(f"    説明: {sample.description}")
            print(f"    価格: {sample.unlock_coins}コイン")
            print(f"    画像: {sample.image_path}")
else:
    print("⚠️  アクセサリーデータがありません")
    print("\n対処方法:")
    print("  python manage.py migrate")

print("\n" + "="*50)
