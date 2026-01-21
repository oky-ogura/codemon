"""グループテーブルのシーケンスと最大IDを確認し、必要なら修正するスクリプト"""
import os
import sys

# PostgreSQLを使用するように環境変数を設定
os.environ['DB_NAME'] = 'codemon'
os.environ['DB_USER'] = 'postgres'
os.environ['DB_PASSWORD'] = 'baretto'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '5432'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')

import django
django.setup()

from django.db import connection

def check_and_fix_sequence():
    with connection.cursor() as cursor:
        # 現在の最大IDを取得
        cursor.execute('SELECT MAX(group_id) FROM "group"')
        max_id = cursor.fetchone()[0]
        print(f"テーブル内の最大 group_id: {max_id}")
        
        # シーケンスの現在値を取得
        cursor.execute('SELECT last_value, is_called FROM group_group_id_seq')
        row = cursor.fetchone()
        seq_value = row[0]
        is_called = row[1]
        print(f"シーケンスの現在値: {seq_value}, is_called: {is_called}")
        
        # 次に使用されるIDを計算
        if is_called:
            next_id = seq_value + 1
        else:
            next_id = seq_value
        print(f"次に生成されるID: {next_id}")
        
        # max_idが存在し、next_idがmax_id以下の場合は修正が必要
        if max_id is not None and next_id <= max_id:
            new_seq_value = max_id + 1
            print(f"\n⚠️ シーケンスが遅れています！")
            print(f"シーケンスを {new_seq_value} に更新します...")
            
            cursor.execute(f"SELECT setval('group_group_id_seq', {new_seq_value}, false)")
            print(f"✅ シーケンスを更新しました。次のIDは {new_seq_value} になります。")
            
            # 確認
            cursor.execute('SELECT last_value, is_called FROM group_group_id_seq')
            row = cursor.fetchone()
            print(f"更新後のシーケンス値: {row[0]}, is_called: {row[1]}")
        else:
            print(f"\n✅ シーケンスは正常です。")

if __name__ == '__main__':
    check_and_fix_sequence()
