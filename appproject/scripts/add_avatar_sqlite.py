import sqlite3
import shutil
import os
p='db.sqlite3'
if os.path.exists(p):
    shutil.copy2(p, p+'.pre_avatar')
    print('backup created:', p+'.pre_avatar')
else:
    print('db not found')

conn=sqlite3.connect(p)
c=conn.cursor()
c.execute("PRAGMA table_info('account')")
cols=[r[1] for r in c.fetchall()]
print('cols:',cols)
if 'avatar' in cols:
    print('avatar already present')
else:
    try:
        c.execute('ALTER TABLE "account" ADD COLUMN "avatar" VARCHAR(255)')
        conn.commit()
        print('avatar column added')
    except Exception as e:
        print('ERROR adding avatar:', e)
conn.close()
