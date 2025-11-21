"""
システム要素テーブルをPostgreSQLに作成するスクリプト
"""
import os
import sys
import django

# Django設定を読み込む
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from django.db import connection

def apply_system_elements_sql():
    """system_element テーブルを作成する"""
    
    sql_file_path = os.path.join(
        os.path.dirname(__file__),
        'sql',
        'create_system_element.sql'
    )
    
    print(f"SQLファイルを読み込み中: {sql_file_path}")
    
    if not os.path.exists(sql_file_path):
        print(f"エラー: SQLファイルが見つかりません: {sql_file_path}")
        return False
    
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    try:
        with connection.cursor() as cursor:
            print("SQLを実行中...")
            cursor.execute(sql)
            print("✓ system_element テーブルが正常に作成されました")
            
            # テーブル構造を確認
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'system_element'
                ORDER BY ordinal_position;
            """)
            
            print("\n=== system_element テーブル構造 ===")
            for row in cursor.fetchall():
                col_name, data_type, is_nullable, default = row
                nullable = "NULL可" if is_nullable == 'YES' else "NOT NULL"
                default_str = f" DEFAULT {default}" if default else ""
                print(f"  {col_name:25s} {data_type:20s} {nullable:10s}{default_str}")
            
            # インデックスを確認
            cursor.execute("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'system_element';
            """)
            
            print("\n=== インデックス ===")
            for row in cursor.fetchall():
                index_name, index_def = row
                print(f"  {index_name}")
            
            return True
            
    except Exception as e:
        print(f"エラー: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("システム要素テーブル作成スクリプト")
    print("=" * 60)
    
    success = apply_system_elements_sql()
    
    if success:
        print("\n✓ 処理が正常に完了しました")
        print("\n次のステップ:")
        print("  1. python manage.py makemigrations codemon")
        print("  2. python manage.py migrate codemon")
    else:
        print("\n✗ 処理中にエラーが発生しました")
        sys.exit(1)
