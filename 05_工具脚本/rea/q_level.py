# -*- coding: utf-8 -*-
"""从 Users.payload 里找等级/经验"""
import json
import re
import sqlite3

DB = r"D:\BH3\7.0\server-v2\run\data\pemukul.sqlite"
con = sqlite3.connect(DB)
cur = con.cursor()
rows = cur.execute("select id,uid,name,length(payload),payload from Users").fetchall()
print("Users 共 %d 行" % len(rows))
for i, uid, name, ln, payload in rows:
    txt = payload if isinstance(payload, str) else payload.decode("utf-8", "replace")
    lv = re.search(r'"[Ll]evel"\s*:\s*(\d+)', txt)
    ex = re.search(r'"[Ee]xp"\s*:\s*(\d+)', txt)
    print("  id=%-3s uid=%-6s name=%-10s payload=%d B  Level=%s  Exp=%s"
          % (i, uid, name, ln, lv.group(1) if lv else "?", ex.group(1) if ex else "?"))
    if i == 1:
        print("    payload 片段:", txt[:300])
con.close()
