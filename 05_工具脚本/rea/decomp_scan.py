# -*- coding: utf-8 -*-
"""解压扫描：在 .wmv 的 LZ4 流中查找明文模式，定位预制体所在包。

锚点法：以 CAB- 为锚，试探 +32..+80 作为 LZ4 体起点，
解压后搜索模式。命中即记录 (包, 体偏移, 模式)。
"""
import os, sys, time, struct
sys.path.insert(0, r"D:\Carol-start\_rea")
from lz4src import lz4_srcmap
from lz4block import lz4_block_decompress

ASB = r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc"
WIN = 48


def bodies(raw, max_anchor=400):
    """返回候选体偏移列表"""
    offs = []
    i = 0
    while True:
        i = raw.find(b"CAB-", i)
        if i < 0:
            break
        offs.append(i)
        i += 4
        if len(offs) >= max_anchor:
            break
    cands = set()
    for o in offs:
        for d in range(32, 32 + WIN):
            cands.add(o + d)
    return sorted(cands)


def try_body(raw, off):
    if off + 40 > len(raw):
        return None
    probe = lz4_block_decompress(raw[off:off + 40])
    if len(probe) < 24:
        return None
    ms, fs, ver, do = struct.unpack_from(">IIII", probe, 0)
    if ver != 17 or not (0 < ms < (1 << 20)) or not (0 < fs < (1 << 26)) or do < ms or do > fs:
        return None
    body, _, _, _ = lz4_srcmap(raw[off:])
    if len(body) < fs:
        return None
    return body


if __name__ == "__main__":
    pats = [a.encode() for a in (sys.argv[1:] or ["worldmapuimanager", "WorldMapUIManager"])]
    files = sorted(f for f in os.listdir(ASB) if f.endswith(".wmv"))
    t0 = time.time()
    for n, f in enumerate(files):
        p = os.path.join(ASB, f)
        raw = open(p, "rb").read()
        seen = set()
        hits = []
        for off in bodies(raw):
            body = try_body(raw, off)
            if body is None:
                continue
            k = len(body)
            if k in seen:
                continue
            seen.add(k)
            for pat in pats:
                if pat in body:
                    hits.append((off, len(body), pat.decode()))
                    break
        if hits:
            print("%-42s %s" % (f, hits[:4]), flush=True)
        if n % 40 == 0:
            print("  ...%d/%d %.0fs" % (n, len(files), time.time() - t0), flush=True)
    print("完成 %.1fs" % (time.time() - t0))
