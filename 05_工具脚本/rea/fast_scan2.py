# -*- coding: utf-8 -*-
"""全包快速扫描：解压每个 SerializedFile 的元数据段，搜明文模式。

只解到 fileSize 就停（跳过 .resS 像素），速度比全量解压快一个量级。
"""
import os, sys, time, struct
sys.path.insert(0, r"D:\Carol-start\_rea")
from lz4fast import lz4_decode_limit

ASB = r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc"


def probe_fs(raw, off):
    if off + 24 > len(raw):
        return None
    h, _ = lz4_decode_limit(raw[off:off + 48], 24)
    if len(h) < 24:
        return None
    ms, fs, ver, do = struct.unpack_from(">IIII", h, 0)
    if ver != 17 or not (0 < ms < (1 << 20)) or not (0 < fs < (1 << 27)) or do < ms or do > fs:
        return None
    return fs


def scan_file(path, pats, budget=64 << 20):
    raw = open(path, "rb").read()
    hits = []
    spent = 0
    i = 0
    while spent < budget:
        i = raw.find(b"CAB-", i)
        if i < 0:
            break
        found = False
        for d in range(32, 32 + 48):
            off = i + d
            fs = probe_fs(raw, off)
            if fs is None:
                continue
            found = True
            body, _ = lz4_decode_limit(raw[off:], fs)
            spent += len(body)
            for p in pats:
                if p in body:
                    hits.append((off, fs, p.decode()))
            break
        i += 4
    return hits, spent


if __name__ == "__main__":
    args = sys.argv[1:]
    pats = [a.encode() for a in args] or [b"WorldMapUIManager"]
    files = sorted(f for f in os.listdir(ASB) if f.endswith(".wmv"))
    if os.environ.get("ONLY"):
        want = set(os.environ["ONLY"].split(","))
        files = [f for f in files if f in want]
    t0 = time.time()
    total = 0
    for n, f in enumerate(files):
        hits, spent = scan_file(os.path.join(ASB, f), pats)
        total += spent
        if hits:
            print("%-42s %s" % (f, hits[:5]), flush=True)
        if n % 20 == 0:
            print("  ...%d/%d %.0fs 已解 %.0fMB" % (n, len(files), time.time() - t0, total / 1e6), flush=True)
    print("完成 %.1fs, 解压总量 %.0fMB" % (time.time() - t0, total / 1e6))
