import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# system_elementテーブルを作成
create_table_sql = """
CREATE TABLE IF NOT EXISTS system_element (
    element_id INTEGER PRIMARY KEY AUTOINCREMENT,
    system_id INTEGER NOT NULL,
    element_type VARCHAR(50) NOT NULL,
    element_label VARCHAR(200),
    element_value TEXT,
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    width INTEGER,
    height INTEGER,
    style_data TEXT,
    element_config TEXT,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (system_id) REFERENCES system(system_id) ON DELETE CASCADE
);
"""

cursor.execute(create_table_sql)
conn.commit()
print("✅ system_elementテーブルを作成しました")

# 確認
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='system_element'")
result = cursor.fetchone()
print(f"確認: system_element テーブル存在 = {result is not None}")

conn.close()
