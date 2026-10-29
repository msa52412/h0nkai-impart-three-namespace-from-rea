"""在指定 .wmv 的压缩态里找关键字并 dump 上下文。"""
import os
import re
import sys

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"

TARGETS = sys.argv[1:] or ["d32bbcfd7e8b0a0f62280267de639b89.wmv",
                           "7a5fb2392be488cdc738e7693080cd81.wmv",
                           "10d8f3adca3f6d9c0c321cbcf89c72b0.wmv",
                           "f5ee331203a685423e94d1bec0bbdb4e.wmv",
                           "5ca670844a1a73364a8ac9d00bfab2c0.wmv",
                           "6d45a4650aab5060c5c31b5431e37bc8.wmv"]

KEYS = ["迪拉克".encode(), "狄拉克".encode(), b"Dirac", b"dirac",
        b"Cover_Title", b"Quantum", b"Abyss"]

for fn in TARGETS:
    p = os.path.join(BASE, fn)
    if not os.path.exists(p):
        print("缺文件", fn)
        continue
    data = open(p, 'rb').read()
    print("=" * 96)
    print("%s  %d bytes" % (fn, len(data)))
    for k in KEYS:
        st = 0
        n = 0
        while n < 6:
            i = data.find(k, st)
            if i < 0:
                break
            ctx = data[max(0, i - 48):i + 64]
            vis = re.sub(rb"[^\x20-\x7e\x80-\xff]", b".", ctx)
            print("  %-14s @%-9d %r" % (k.decode("utf-8", "replace"), i, vis))
            st = i + 1
            n += 1
        if n == 0 and k not in (b"Cover_Title",):
            pass
