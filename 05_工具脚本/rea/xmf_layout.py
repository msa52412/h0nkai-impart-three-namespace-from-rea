# -*- coding: utf-8 -*-
import os, struct
ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
d = open(os.path.join(ASB, "BlockMeta.xmf"), "rb").read()

names = ["60dc984965f6694109d808d48e53616b","7b08427f6f268e9980ca84fe2552e9d3",
         "0cef4f93d7b346d542b472d4980e1099","971e62e94b623083fcc12464537b285c",
         "3844a431cfc9c8a34c9cddb043a1eacb","7019a1ae1f84c4f264ff17012d35e6e1"]
pos = []
for n in names:
    i = d.find(bytes.fromhex(n))
    pos.append(i)
    print("%s -> %d" % (n, i))
print("\n相邻差值:", [pos[i+1]-pos[i] for i in range(len(pos)-1)])

# 目标
t = d.find(bytes.fromhex("f65865df27ea6a9e58bf8f1f3b01bdcd"))
print("目标 ->", t)

# 若步长 32，起点 = pos[0] - k
for k in range(32):
    if all((p - pos[0]) % 32 == 0 for p in pos if p >= 0):
        pass
base = pos[0]
print("\n以第一条 md5 为基准，各条相对偏移:", [p - base for p in pos])
print("目标相对偏移:", t - base)
