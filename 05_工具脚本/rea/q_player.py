# -*- coding: utf-8 -*-
"""查服务端存档里的玩家等级 / Exp"""
import glob
import os
import sqlite3

cands = glob.glob(r"D:\BH3\7.0\server-v2\run\data\*.sqlite") + \
        glob.glob(r"D:\BH3\7.0\server-v2\run\data\*.db")
cands = sorted(set(cands))
print("找到 %d 个 db 文件" % len(cands))
for p in cands:
    print(" ", p, os.path.getsize(p), "B")

if not cands:
    raise SystemExit(1)

db = max(cands, key=os.path.getsize)
print("\n使用:", db)
con = sqlite3.connect(db)
cur = con.cursor()
tables = [r[0] for r in cur.execute(
    "select name from sqlite_master where type='table'")]
print("表:", tables)

for t in tables:
    cols = [r[1] for r in cur.execute("PRAGMA table_info(%s)" % t)]
    hit = [c for c in cols if c.lower() in ("level", "exp", "uid", "id", "nick", "name")]
    if not hit:
        continue
    print("\n== %s ==  列=%s" % (t, cols[:24]))
    try:
        rows = cur.execute("select %s from %s limit 6"
                           % (",".join(hit), t)).fetchall()
        for r in rows:
            print("   ", dict(zip(hit, r)))
    except Exception as e:
        print("   查询失败:", e)
con.close()
