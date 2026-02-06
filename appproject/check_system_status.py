"""
システム機能動作確認スクリプト
各機能の基本的な動作をチェックします
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from codemon.models import System, Algorithm, Checklist, ChecklistGroup, Accessory, Achievement
from accounts.models import Account

print("="*70)
print("システム機能動作確認")
print("="*70)

# データベース接続確認
print("\n【1. データベース接続確認】")
try:
    user_count = Account.objects.count()
    print(f"✅ データベース接続: OK")
    print(f"   登録ユーザー数: {user_count}名")
except Exception as e:
    print(f"❌ データベース接続エラー: {e}")

# 各テーブルのデータ確認
print("\n【2. マスターデータ確認】")
tables = [
    ("実績", Achievement),
    ("アクセサリー", Accessory),
]

for name, model in tables:
    try:
        count = model.objects.count()
        status = "✅" if count > 0 else "⚠️"
        print(f"{status} {name}: {count}件")
    except Exception as e:
        print(f"❌ {name}テーブルエラー: {e}")

# ユーザーデータ確認
print("\n【3. ユーザーデータ確認】")
user_tables = [
    ("システム", System),
    ("アルゴリズム", Algorithm),
    ("チェックリスト", Checklist),
    ("グループ", ChecklistGroup),
]

for name, model in user_tables:
    try:
        count = model.objects.count()
        print(f"   {name}: {count}件")
    except Exception as e:
        print(f"❌ {name}テーブルエラー: {e}")

# 主要機能URL一覧
print("\n【4. 主要機能URL一覧】")
print("\n開発サーバーが起動中の場合、以下のURLにアクセスして確認してください：")
print("\n📋 基本機能:")
print("   - ホーム: http://127.0.0.1:8000/")
print("   - システム一覧: http://127.0.0.1:8000/accounts/system/list/")
print("\n🎮 ゲーム要素:")
print("   - 実績（トロフィー）: http://127.0.0.1:8000/codemon/achievements/")
print("   - ショップ: http://127.0.0.1:8000/codemon/accessories/")
print("\n📝 チェックリスト:")
print("   - チェックリスト一覧: http://127.0.0.1:8000/codemon/checklists/")
print("   - チェックリスト選択: http://127.0.0.1:8000/codemon/checklists/selection/")
print("\n👥 グループ:")
print("   - グループ一覧: http://127.0.0.1:8000/codemon/groups/")
print("\n💬 AI会話:")
print("   - AI会話: http://127.0.0.1:8000/codemon/threads/")

print("\n" + "="*70)
print("確認完了")
print("="*70)
print("\n⚠️ 各URLにアクセスして、エラーが出ないか確認してください。")
print("問題がある機能があれば、エラーメッセージを確認してください。")
