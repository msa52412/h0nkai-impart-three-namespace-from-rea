# -*- coding: utf-8 -*-
"""从服务端日志里提取 Challenge/Task_N 点击 -> 随后进入的页面"""
import re, io, collections

L = r"D:/BH3/7.0/_launch/logs/v2_Server.log"
pat_click = re.compile(r"Click [^,;]*Challenge/(Task_\d+)/Cover,(\d+)")
pat_enter = re.compile(r"Enter ([A-Za-z0-9_]+PageContext),(\d+)")

data = io.open(L, encoding="utf-8", errors="replace").read()
# 按 PlayerLog 分段
segments = re.split(r"ClientReport \| PlayerLog =", data)
res = collections.defaultdict(collections.Counter)
for seg in segments[1:]:
    events = []
    for m in re.finditer(r"(Click [^,;]*Challenge/(Task_\d+)/Cover|Enter ([A-Za-z0-9_]+PageContext)),?(\d+)?", seg):
        pass
    # 简单顺序扫描
    toks = []
    for m in re.finditer(r"Click ([^,;]+),(\d+)|Enter ([A-Za-z0-9_]+PageContext),(\d+),|Exit ([A-Za-z0-9_]+PageContext),(\d+)", seg):
        if m.group(1):
            toks.append(("click", m.group(1), int(m.group(2))))
        elif m.group(3):
            toks.append(("enter", m.group(3), int(m.group(4))))
        else:
            toks.append(("exit", m.group(5), int(m.group(6))))
    for i, (k, v, t) in enumerate(toks):
        if k != "click": continue
        m = re.search(r"Challenge/(Task_\d+)/Cover", v)
        if not m: continue
        task = m.group(1)
        nxt = "(无)"
        for j in range(i+1, min(i+6, len(toks))):
            if toks[j][0] == "enter":
                nxt = toks[j][1]; break
            if toks[j][0] == "click":
                break
        res[task][nxt] += 1

print("Challenge/Task_N 点击 -> 随后进入的页面")
for task in sorted(res, key=lambda x: int(x.split('_')[1])):
    print("  %-8s %s" % (task, dict(res[task])))
