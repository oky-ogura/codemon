# ...existing code...
import os
import psycopg2

host = os.getenv('DB_HOST', 'localhost')
user = os.getenv('DB_USER', 'postgres')
dbname = os.getenv('DB_NAME', 'codemon')
pwd = os.getenv('DB_PASSWORD')  # ここは None になりうる

def check_db_connection():
    """インポート時に実行されないよう関数化"""
    if not pwd:
        print("DB_PASSWORD not set; skipping connection check.")
        return None
    print("Connecting with:", {'host': host, 'user': user, 'dbname': dbname, 'has_password': bool(pwd)})
    conn = psycopg2.connect(host=host, user=user, dbname=dbname, password=pwd)
    return conn

if __name__ == '__main__':
    # 手動で実行する時だけ接続する
    check_db_connection()
# ...existing code...