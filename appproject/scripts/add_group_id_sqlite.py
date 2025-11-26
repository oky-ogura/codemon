#!/usr/bin/env python3
"""Add `group_id` INTEGER column to `account` table in local SQLite DB if missing.

Creates a backup `db.sqlite3.pre_groupid` before altering.
Run from project root (appproject) with the virtualenv python.
"""
import os
import shutil
import sqlite3

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE, 'db.sqlite3')
BACKUP_PATH = os.path.join(BASE, 'db.sqlite3.pre_groupid')

if not os.path.exists(DB_PATH):
    print('DB not found at', DB_PATH)
    raise SystemExit(1)

print('Backing up', DB_PATH, '->', BACKUP_PATH)
shutil.copy2(DB_PATH, BACKUP_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
try:
    cur.execute("PRAGMA table_info('account')")
    cols = [r[1] for r in cur.fetchall()]
    print('Existing columns:', cols)
    if 'group_id' in cols:
        print('group_id already exists; no action taken.')
    else:
        print('Adding group_id INTEGER column to account table...')
        cur.execute('ALTER TABLE account ADD COLUMN group_id INTEGER')
        conn.commit()
        print('Added group_id column.')
except Exception as e:
    print('Error while altering table:', e)
    conn.rollback()
    raise
finally:
    cur.close()
    conn.close()
