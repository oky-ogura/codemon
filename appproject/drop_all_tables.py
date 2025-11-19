"""
Drop all tables in the database via Django ORM connection.
Run with: python drop_all_tables.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public';
    """)
    tables = cursor.fetchall()
    
    for (table,) in tables:
        print(f"Dropping table: {table}")
        cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE;')
    
    print("All tables dropped. Run: python manage.py migrate")
