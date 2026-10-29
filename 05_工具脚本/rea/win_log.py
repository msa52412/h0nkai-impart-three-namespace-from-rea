# -*- coding: utf-8 -*-
"""打印指定时间点的原始日志窗口，含 retcode / 错误。"""
import io, sys, re

LOG = r"D:\BH3\7.0\_launch\logs\v2_Server.log"

def window(t0, t1):
    raw = io.open(LOG, "r", encoding="utf-8", errors="replace").read()
    out = []
    for ln in raw.splitlines():
        m = re.match(r"(\d\d:\d\d:\d\d)", ln.strip())
        if m and t0 <= m.group(1) <= t1:
            out.append(ln.rstrip())
    return out

if __name__ == "__main__":
    t0 = sys.argv[1] if len(sys.argv) > 1 else "17:18:40"
    t1 = sys.argv[2] if len(sys.argv) > 2 else "17:19:30"
    ws = window(t0, t1)
    print("行数:", len(ws))
    for ln in ws:
        print(ln[:200])
