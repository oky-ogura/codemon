"""
グループテーブルのシーケンスを修正するスクリプト
"""
import os
import psycopg2

# DB接続情報
conn = psycopg2.connect(
    host='localhost',
    database='codemon',
    user='codemon',
    password=os.environ.get('DB_PASSWORD', 'baretto')
)
conn.autocommit = True
cur = conn.cursor()

# 現在の最大group_idを取得
cur.execute('SELECT MAX(group_id) FROM "group"')
max_id = cur.fetchone()[0]
print(f'現在の最大 group_id: {max_id}')

# シーケンスの現在値を確認
try:
    cur.execute("SELECT last_value FROM group_group_id_seq")
    seq_val = cur.fetchone()[0]
    print(f'シーケンス group_group_id_seq の last_value: {seq_val}')
except Exception as e:
    print(f'シーケンス group_group_id_seq が見つからない: {e}')
    seq_val = None

# 他のシーケンス名を試す
for seq_name in ['group_id_seq', 'group_group_id_seq', 'public.group_group_id_seq']:
    try:
        cur.execute(f"SELECT last_value FROM {seq_name}")
        val = cur.fetchone()[0]
        print(f'シーケンス {seq_name} の last_value: {val}')
    except Exception as e:
        print(f'シーケンス {seq_name}: {e}')

# シーケンスを適切な値にリセット
if max_id is not None:
    new_val = max_id + 1
    print(f'\nシーケンスを {new_val} にリセットします...')
    try:
        cur.execute(f"SELECT setval('group_group_id_seq', {new_val}, false)")
        print('group_group_id_seq をリセットしました')
    except Exception as e:
        print(f'リセット失敗 (group_group_id_seq): {e}')
        try:
            cur.execute(f"SELECT setval('group_id_seq', {new_val}, false)")
            print('group_id_seq をリセットしました')
        except Exception as e2:
            print(f'リセット失敗 (group_id_seq): {e2}')

# 確認
print('\n--- リセット後の確認 ---')
for seq_name in ['group_group_id_seq', 'group_id_seq']:
    try:
        cur.execute(f"SELECT last_value FROM {seq_name}")
        val = cur.fetchone()[0]
        print(f'シーケンス {seq_name} の last_value: {val}')
    except:
        pass

cur.close()
conn.close()
print('\n完了!')
