# -*- coding: utf-8 -*-
"""用 PlayerLevelData.json 把 Exp 换算成等级"""
import glob
import json
import os

CAND = glob.glob(r"D:\BH3\7.0\server-v2\run\Resources\ExcelOutputAsset\PlayerLevel*.json")
print("等级表候选:", CAND)
if not CAND:
    raise SystemExit(1)

rows = json.load(open(CAND[0], encoding="utf-8"))
print("行数", len(rows), "列", list(rows[0].keys()))

# 找字段名
exp_key = None
for k in rows[0]:
    if "exp" in k.lower():
        exp_key = k
        break
lvl_key = None
for k in rows[0]:
    if k.lower() in ("level", "lev", "id"):
        lvl_key = k
        break
print("exp_key=%r lvl_key=%r" % (exp_key, lvl_key))

# 每级的累计经验阈值
pairs = sorted(((r.get(exp_key) or 0, r.get(lvl_key) or 0) for r in rows))
print("前 5:", pairs[:5], " 后 5:", pairs[-5:])


def level_of(exp):
    lv = 1
    for need, l in pairs:
        if exp >= need:
            lv = l
        else:
            break
    return lv


for uid, name, exp in [(1002, "1", 300257), (1003, "tianjige", 100),
                       (1004, "100", 108578), (1001, "test", 0)]:
    print("  uid=%s name=%-10s Exp=%-8d -> Level %d" % (uid, name, exp, level_of(exp)))
