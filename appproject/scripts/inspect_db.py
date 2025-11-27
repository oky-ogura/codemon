import sqlite3

p='db.sqlite3'
conn=sqlite3.connect(p)
c=conn.cursor()
for t in ['account','group','codemon_group','auth_user','accounts_account','codemon_groupmember']:
    try:
        c.execute(f"PRAGMA table_info({t})")
        cols=[r[1] for r in c.fetchall()]
        print('TABLE',t,cols)
    except Exception as e:
        print('TABLE',t,'ERROR',e)
conn.close()
