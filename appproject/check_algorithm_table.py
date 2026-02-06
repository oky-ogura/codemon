import sqlite3
import os
import django

# Django設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

# データベース接続
db_path = 'db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# algorithmテーブルの構造を確認
print("=" * 60)
print("algorithm テーブルの構造:")
print("=" * 60)
cursor.execute("PRAGMA table_info(algorithm)")
columns = cursor.fetchall()

if columns:
    print(f"\n全カラム数: {len(columns)}")
    print("\n| ID | カラム名 | 型 | NULL許可 | デフォルト値 | 主キー |")
    print("|" + "-" * 58 + "|")
    for col in columns:
        print(f"| {col[0]} | {col[1]} | {col[2]} | {col[3]} | {col[4]} | {col[5]} |")
    
    # blockly_xmlカラムの存在確認
    column_names = [col[1] for col in columns]
    if 'blockly_xml' in column_names:
        print("\n✅ blockly_xml カラムは存在します")
    else:
        print("\n❌ blockly_xml カラムが見つかりません")
        print("\n現在のカラム一覧:")
        for name in column_names:
            print(f"  - {name}")
else:
    print("❌ algorithm テーブルが見つかりません")

# マイグレーション状態を確認
print("\n" + "=" * 60)
print("適用済みマイグレーション (codemon アプリ):")
print("=" * 60)
cursor.execute("SELECT name FROM django_migrations WHERE app='codemon' ORDER BY id")
migrations = cursor.fetchall()
for mig in migrations:
    print(f"  ✓ {mig[0]}")

conn.close()
