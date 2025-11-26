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
    if 'avatar' not in cols:
        print('avatar not found — adding column')
        # In SQLite, store ImageField path as TEXT
        c.execute("ALTER TABLE account ADD COLUMN avatar TEXT")
        print('avatar column added')
    else:
        print('avatar column already exists')
