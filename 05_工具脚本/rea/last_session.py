# -*- coding: utf-8 -*-
"""只解析最后一次登录会话的点击序列与页面进出。"""
import io, re

LOG = r"D:\BH3\7.0\_launch\logs\v2_Server.log"
raw = io.open(LOG, "r", encoding="utf-8", errors="replace").read()
lines = raw.splitlines()

# 找最后一次 PlayerLoginReq
last_login = -1
for i, ln in enumerate(lines):
    if "PlayerLoginReq" in ln:
        last_login = i
print("最后一次登录在第 %d 行 / 共 %d 行" % (last_login, len(lines)))

events = []
for ln in lines[last_login:]:
    if "PlayerLog" not in ln:
        continue
    ts = re.match(r"(\d\d:\d\d:\d\d)", ln.strip())
    ts = ts.group(1) if ts else "?"
    body = ln.split("PlayerLog =", 1)[1] if "PlayerLog =" in ln else ""
    for p in [x.strip() for x in body.split(";") if x.strip()]:
        events.append((ts, p))

print("事件数 %d\n" % len(events))
for ts, e in events:
    # 只保留点击与页面进出
    if e.startswith("Click") or "Enter" in e or "Exit" in e:
        # 简化路径
        e2 = re.sub(r"WorldMapUIManager_V2\(Clone\)/Canvas3D/", "", e)
        e2 = re.sub(r"MainCanvas/Pages/MainPage\(Clone\)/", "", e2)
        print("%s  %s" % (ts, e2[:150]))
