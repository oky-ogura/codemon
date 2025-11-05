
# ...existing code...
import os
import psycopg2

def main():
    # PGPASSWORD と DB_PASSWORD の両方を許容
    host = os.environ.get("DB_HOST", "localhost")
    user = os.environ.get("DB_USER", "postgres")
    dbname = os.environ.get("DB_NAME", "codemon")
    pwd = os.environ.get("PGPASSWORD") or os.environ.get("DB_PASSWORD")

    print("Connecting with:", {"host": host, "user": user, "dbname": dbname, "has_password": bool(pwd)})

    conn = psycopg2.connect(host=host, user=user, dbname=dbname, password=pwd)
    cur = conn.cursor()
    cur.execute("SELECT current_database(), inet_server_addr(), inet_server_port(), version()")
    print("server info:", cur.fetchone())

    cur.execute("""
    SELECT table_schema, table_name
    FROM information_schema.tables
    WHERE table_schema NOT IN ('information_schema','pg_catalog')
    ORDER BY table_schema, table_name
    """)
    tables = cur.fetchall()
    print("tables in this DB:", tables if tables else "NO TABLES")

    cur.close()
    conn.close()

if __name__ == '__main__':
    main()

