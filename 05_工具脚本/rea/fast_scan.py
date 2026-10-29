# -*- coding: utf-8 -*-
"""快速解压扫描（C 版 lz4）。

对每个 .wmv：以 CAB- 为锚，试探体起点，解压 SerializedFile 部分
（只需 fileSize 字节，不需要 .resS 像素），在明文里搜模式。
"""
import os, sys, time, struct
import lz4.block

ASB = r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc"


def probe_fs(raw, off):
    """解出 SF 头，返回 fileSize；失败返回 None"""
    if off + 24 > len(raw):
        return None
    try:
        h = lz4.block.decompress(raw[off:off + 64], uncompressed_size=64)
    except Exception:
        return None
    if len(h) < 24:
        return None
    ms, fs, ver, do = struct.unpack_from(">IIII", h, 0)
    if ver != 17 or not (0 < ms < (1 << 20)) or not (0 < fs < (1 << 27)) or do < ms or do > fs:
        return None
    return fs


def sf_body(raw, off, fs):
    try:
        return lz4.block.decompress(raw[off:], uncompressed_size=fs)
    except Exception:
        return None


def scan_file(path, pats, max_anchor=600):
    raw = open(path, "rb").read()
    hits = []
    seen_off = set()
    i = 0
    n_anchor = 0
    while n_anchor < max_anchor:
        i = raw.find(b"CAB-", i)
        if i < 0:
            break
        n_anchor += 1
        for d in range(32, 32 + 48):
            off = i + d
            if off in seen_off:
                continue
            fs = probe_fs(raw, off)
            if fs is None:
                continue
            seen_off.add(off)
            body = sf_body(raw, off, fs)
            if body is None:
                continue
            for p in pats:
                if p in body:
                    hits.append((off, fs, p.decode()))
            break
        i += 4
    return hits


if __name__ == "__main__":
    pats = [a.encode() for a in (sys.argv[1:] or ["WorldMapUIManager"])]
    files = sorted(f for f in os.listdir(ASB) if f.endswith(".wmv"))
    t0 = time.time()
    for n, f in enumerate(files):
        hits = scan_file(os.path.join(ASB, f), pats)
        if hits:
            print("%-42s %s" % (f, hits[:5]), flush=True)
        if n % 25 == 0:
            print("  ...%d/%d %.0fs" % (n, len(files), time.time() - t0), flush=True)
    print("完成 %.1fs" % (time.time() - t0))
