import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from django.db import connection

print('Checking account table columns...')
with connection.cursor() as c:
    c.execute("PRAGMA table_info(account)")
    rows = c.fetchall()
    cols = [r[1] for r in rows]
    print('columns:', cols)
    if 'age' not in cols:
        print('age not found — adding column')
        c.execute('ALTER TABLE account ADD COLUMN age integer')
        print('age column added')
    else:
        print('age column already exists')
