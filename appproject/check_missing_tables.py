"""
不足しているテーブルを確認するスクリプト
"""
import sqlite3

# データベース内のテーブルを取得
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
existing_tables = {row[0] for row in cursor.fetchall()}
conn.close()

# マイグレーションで定義されているモデル（モデル名 -> テーブル名）
expected_models = {
    'AIConversation': 'codemon_aiconversation',
    'AIMessage': 'codemon_aimessage',
    'Algorithm': 'algorithm',
    'ChatMessage': 'chat_message',
    'ChatAttachment': 'chat_attachment',
    'ChatThread': 'chat_thread',
    'ChatScore': 'chat_score',
    'Checklist': 'checklist',
    'ChecklistItem': 'checklist_item',
    'Group': None,  # 複数のグループテーブルがあるため除外
    'GroupMember': None,
    'ReadReceipt': 'chat_read_receipt',
    'System': 'system',
    'SystemElement': 'system_element'
}

print("=" * 80)
print("テーブル存在確認")
print("=" * 80)

missing_tables = []
for model_name, table_name in expected_models.items():
    if table_name is None:
        continue
    
    if table_name in existing_tables:
        print(f"✅ {table_name} (モデル: {model_name})")
    else:
        print(f"❌ {table_name} (モデル: {model_name}) - 不足")
        missing_tables.append(table_name)

if missing_tables:
    print(f"\n不足しているテーブル数: {len(missing_tables)}")
    print("不足しているテーブル:")
    for table in missing_tables:
        print(f"  - {table}")
else:
    print("\n✅ すべてのテーブルが存在します")

print("\n" + "=" * 80)
