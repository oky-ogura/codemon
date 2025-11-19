import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_NAME = os.environ.get('DB_NAME', 'codemon')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'Fujita0728')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')

try:
    conn = psycopg2.connect(
        dbname='postgres', user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    print(f"Dropping database: {DB_NAME}")
    cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")
    print("Drop done")

    print(f"Creating database: {DB_NAME}")
    cur.execute(f"CREATE DATABASE {DB_NAME};")
    print("Create done")

    cur.close()
    conn.close()
    print("Reset completed. Next: python manage.py migrate")
except Exception as e:
    print(f"Error: {e}")
