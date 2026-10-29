# -*- coding: utf-8 -*-
"""展开 PlayerLog 为逐条事件（Enter/Exit/Click），便于看清 UI 结构。"""
import io, sys, re

LOG = r"D:\BH3\7.0\_launch\logs\v2_Server.log"

def dump(t0=None, t1=None, only_abyss=False):
    raw = io.open(LOG, "r", encoding="utf-8", errors="replace").read()
    for ln in raw.splitlines():
        m = re.match(r"(\d\d:\d\d:\d\d)", ln.strip())
        if not m:
            continue
        ts = m.group(1)
        if t0 and ts < t0: continue
        if t1 and ts > t1: continue
        if "PlayerLog" not in ln:
            continue
        # 取出 = 之后的载荷
        body = ln.split("PlayerLog =", 1)[1] if "PlayerLog =" in ln else ln
        parts = [p.strip() for p in body.split(";") if p.strip()]
        for p in parts:
            if only_abyss and not re.search(r"Abyss|Endless|Task_|OpenWorld", p, re.I):
                continue
            print("%s  %s" % (ts, p[:160]))

if __name__ == "__main__":
    t0 = sys.argv[1] if len(sys.argv) > 1 else None
    t1 = sys.argv[2] if len(sys.argv) > 2 else None
    ob = len(sys.argv) > 3 and sys.argv[3] == "abyss"
    dump(t0, t1, ob)
