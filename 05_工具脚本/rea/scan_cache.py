# -*- coding: utf-8 -*-
import os, sys
D = r"C:/Users/Administrator/AppData/LocalLow/miHoYo/Honkai Impact 3"
D = r"C:/Users/Administrator/AppData/LocalLow/miHoYo/Honkai Impact 3/Data/data"
PAT = b"settingicon"
hits = []
n = 0
for fn in sorted(os.listdir(D)):
    p = os.path.join(D, fn)
    if not os.path.isfile(p): continue
    n += 1
    try:
        with open(p, "rb") as f:
            data = f.read()
    except Exception as e:
        print("读取失败", fn, e); continue
    if PAT in data:
        hits.append((fn, len(data)))
print("扫描 %d 个缓存文件" % n)
print("含 'settingicon' 的:", hits if hits else "无")
