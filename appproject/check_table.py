import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# system_elementテーブルの確認
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='system_element'")
result = cursor.fetchone()
print(f"system_element テーブル存在: {result is not None}")

# すべてのテーブルを表示
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()
print("\nすべてのテーブル:")
for table in tables:
    print(f"  - {table[0]}")

conn.close()
