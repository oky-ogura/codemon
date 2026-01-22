"""
グループテーブルのシーケンスをリセットするスクリプト
"""
import os
import django

# Django設定を読み込む
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from django.db import connection

def fix_group_sequence():
    with connection.cursor() as cursor:
        # 現在の最大group_idを取得
        cursor.execute('SELECT COALESCE(MAX(group_id), 7000000) FROM "group"')
        max_id = cursor.fetchone()[0]
        
        # シーケンスを次の値にリセット
        next_val = max_id + 1
        cursor.execute(f"SELECT setval('group_group_id_seq', {next_val})")
        new_seq = cursor.fetchone()[0]
        
        print(f'現在の最大group_id: {max_id}')
        print(f'シーケンスを {new_seq} にリセットしました')
        print('次に作成されるグループのIDは:', new_seq)

if __name__ == '__main__':
    fix_group_sequence()


if __name__ == '__main__':
    fix_group_sequence()

