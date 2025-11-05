#!/usr/bin/env python
"""簡易接続確認スクリプト（実行専用）

このスクリプトは直接実行したときだけ PostgreSQL へ接続します。
Django の起動時に自動実行されないように、モジュールとしての副作用は排除しています。
"""
import os
import psycopg2


def main():
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
