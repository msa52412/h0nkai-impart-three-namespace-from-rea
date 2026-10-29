# -*- coding: utf-8 -*-
"""在所有 .wmv 里做原始字节搜索（分块，避免整文件读入）。"""
import os, sys, time

ASB = r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc"
CHUNK = 8 << 20
OVERLAP = 256

def scan(path, pats):
    found = {p: [] for p in pats}
    sz = os.path.getsize(path)
    with open(path, "rb") as f:
        pos = 0
        tail = b""
        while pos < sz:
            blk = f.read(CHUNK)
            if not blk:
                break
            buf = tail + blk
            base = pos - len(tail)
            for p in pats:
                i = 0
                while True:
                    i = buf.find(p, i)
                    if i < 0:
                        break
                    found[p].append(base + i)
                    i += 1
            tail = buf[-OVERLAP:]
            pos += len(blk)
    return found

if __name__ == "__main__":
    pats = [a.encode() for a in (sys.argv[1:] or ["WorldMapUIManager", "MapPanel0"])]
    files = sorted(f for f in os.listdir(ASB) if f.endswith(".wmv"))
    t0 = time.time()
    hit = 0
    for n, f in enumerate(files):
        p = os.path.join(ASB, f)
        r = scan(p, pats)
        tot = sum(len(v) for v in r.values())
        if tot:
            hit += 1
            print("%-42s %s" % (f, {k.decode(): len(v) for k, v in r.items() if v}), flush=True)
        if n % 50 == 0:
            print("  ...%d/%d %.0fs" % (n, len(files), time.time() - t0), flush=True)
    print("完成 %.1fs, 命中包 %d/%d" % (time.time() - t0, hit, len(files)))
