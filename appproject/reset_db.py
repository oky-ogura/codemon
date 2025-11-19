import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

# PostgreSQL接続情報
DB_NAME = os.environ.get('DB_NAME', 'codemon')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'Fujita0728')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')

try:
    # postgresデータベースに接続
    conn = psycopg2.connect(
        dbname='postgres',
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # 既存のデータベースを削除
    print(f"Dropping database '{DB_NAME}'...")
    cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")
    print(f"Database '{DB_NAME}' dropped successfully.")
    
    # 新しいデータベースを作成
    print(f"Creating database '{DB_NAME}'...")
    cursor.execute(f"CREATE DATABASE {DB_NAME};")
    print(f"Database '{DB_NAME}' created successfully.")
    
    cursor.close()
    conn.close()
    
    print("\nDatabase reset completed successfully!")
    print("Now run: python manage.py migrate")
    
except Exception as e:
    print(f"Error: {e}")
