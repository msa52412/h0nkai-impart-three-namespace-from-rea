"""全量扫描：找出所有含 Cover_Title / Dirac / 迪拉克 的 .wmv，并统计具体名字。

分块读（8MB），保留 64 字节重叠，避免漏掉跨界串。
"""
import os
import re
import sys
import time

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
CHUNK = 8 * 1024 * 1024
OVER = 64

KEYS = [b"Cover_Title", b"Dirac", b"dirac",
        "迪拉克".encode("utf-8"), b"Quantum", b"Abyss"]

pat = re.compile(rb"Cover_Title[A-Za-z0-9_]{0,4}")

files = sorted(f for f in os.listdir(BASE) if f.endswith(".wmv"))
print("文件数:", len(files))
tot = sum(os.path.getsize(os.path.join(BASE, f)) for f in files)
print("总大小: %.1f GB" % (tot / 1e9))

hits = {}
names = {}
t0 = time.time()
for i, fn in enumerate(files):
    p = os.path.join(BASE, fn)
    cnt = {k: 0 for k in KEYS}
    nm = {}
    with open(p, 'rb') as fp:
        tail = b""
        while True:
            buf = fp.read(CHUNK)
            if not buf:
                break
            blk = tail + buf
            for k in KEYS:
                c = blk.count(k)
                if c:
                    cnt[k] += c
            for m in pat.finditer(blk):
                s = m.group(0)
                nm[s] = nm.get(s, 0) + 1
            tail = blk[-OVER:]
    if any(cnt.values()):
        hits[fn] = cnt
        names[fn] = nm
    if (i + 1) % 50 == 0:
        print("  ... %d/%d  %.1fs" % (i + 1, len(files), time.time() - t0))

print("\n=== 命中文件 %d 个 ===" % len(hits))
for fn, c in sorted(hits.items(), key=lambda x: -sum(x[1].values())):
    ks = " ".join("%s=%d" % (k.decode("utf-8", "replace"), v)
                  for k, v in c.items() if v)
    print("  %-40s %s" % (fn, ks))
    if names.get(fn):
        print("      names:", dict(sorted(names[fn].items())))
