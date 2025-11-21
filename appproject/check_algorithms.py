import os
import psycopg2

# データベース接続情報
host = os.environ.get("DB_HOST", "localhost")
user = os.environ.get("DB_USER", "postgres")
dbname = os.environ.get("DB_NAME", "codemon")
pwd = os.environ.get("PGPASSWORD") or os.environ.get("DB_PASSWORD")

print(f"Connecting to database: {dbname}@{host}")

try:
    conn = psycopg2.connect(host=host, user=user, dbname=dbname, password=pwd)
    cur = conn.cursor()
    
    # アルゴリズムテーブルの存在確認
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'algorithm'
        );
    """)
    table_exists = cur.fetchone()[0]
    print(f"\nAlgorithm table exists: {table_exists}")
    
    if table_exists:
        # アルゴリズムデータの件数確認
        cur.execute("SELECT COUNT(*) FROM algorithm;")
        count = cur.fetchone()[0]
        print(f"Total algorithms: {count}")
        
        # 最初の10件を表示
        cur.execute("""
            SELECT algorithm_id, user_id, algorithm_name, algorithm_description, created_at, updated_at 
            FROM algorithm 
            ORDER BY updated_at DESC, created_at DESC 
            LIMIT 10;
        """)
        algorithms = cur.fetchall()
        
        if algorithms:
            print("\n=== Algorithm List (最新10件) ===")
            for alg in algorithms:
                print(f"\nID: {alg[0]}")
                print(f"  User ID: {alg[1]}")
                print(f"  Name: {alg[2]}")
                print(f"  Description: {alg[3]}")
                print(f"  Created: {alg[4]}")
                print(f"  Updated: {alg[5]}")
        else:
            print("\nNo algorithms found in database.")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\nError: {e}")
