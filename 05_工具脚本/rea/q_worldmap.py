# -*- coding: utf-8 -*-
"""查 WorldMap.json 里入口的解锁条件与映射"""
import json
from collections import Counter

P = r"D:\BH3\7.0\server-v2\run\Resources\ExcelOutputAsset\WorldMap.json"
rows = json.load(open(P, encoding="utf-8"))
print("总行数", len(rows))

want = {6, 7, 8, 11, 15, 18}
print("\n-- 面板上出现的 + 目标 ID --")
for r in rows:
    if r.get("ID") in want:
        print("ID=%-4s EntryID=%-6s FT=%-9s Unlock=%-4s img=%s"
              % (r.get("ID"), r.get("EntryID"), r.get("FeatureType"),
                 r.get("UnlockLevel"), str(r.get("EntryImagePath"))[:56]))

print("\n-- 全部 EntryID 1001..1013 --")
for r in rows:
    e = r.get("EntryID")
    if isinstance(e, int) and 1001 <= e <= 1013:
        print("EntryID=%-6s ID=%-4s FT=%-9s Unlock=%-4s img=%s"
              % (e, r.get("ID"), r.get("FeatureType"), r.get("UnlockLevel"),
                 str(r.get("EntryImagePath"))[:56]))

print("\n-- UnlockLevel 分布 --")
print(sorted(Counter(r.get("UnlockLevel") for r in rows).items()))

print("\n-- 按 ID 排序的前 24 行 --")
for r in sorted(rows, key=lambda x: (x.get("ID") or 0))[:24]:
    print("ID=%-4s EntryID=%-6s FT=%-9s Unlock=%-4s"
          % (r.get("ID"), r.get("EntryID"), r.get("FeatureType"), r.get("UnlockLevel")))
