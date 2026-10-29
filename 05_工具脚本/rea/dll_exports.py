# -*- coding: utf-8 -*-
import re, os
p = r"D:/BH3/7.0/BH3_Data/Plugins/AssetNativePlugin.dll"
d = open(p, "rb").read()
# 从导出表名字符串里抓
names = sorted(set(m.group(1).decode() for m in re.finditer(rb"([A-Z][A-Za-z0-9_]{4,60})\x00", d)))
kw = ("Block", "File", "Map", "Save", "Write", "Set", "Serialize", "Create", "Get", "Load", "Asb", "Segment")
hits = [n for n in names if any(k in n for k in kw)]
print("导出候选 %d 个:" % len(hits))
for n in hits: print("  ", n)
