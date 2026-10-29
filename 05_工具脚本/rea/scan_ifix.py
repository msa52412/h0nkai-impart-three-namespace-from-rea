# -*- coding: utf-8 -*-
"""在 wmv + Data/data 中搜索 InjectFix 补丁相关资源"""
import os, glob, time

TARGETS = [
    (r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc", "*.wmv"),
    (r"C:\Users\Administrator\AppData\LocalLow\miHoYo\Honkai Impact 3\Data\data", "*.unity3d"),
]
KW = [b"IFixPatch", b"IFix", b"Assembly-CSharp.dll.patch", b"patch-name"]
CHUNK = 8 * 1024 * 1024
OV = 64


def scan(paths, label):
    hits = []
    total = sum(os.path.getsize(p) for p in paths)
    done = 0
    t0 = time.time()
    for p in paths:
        with open(p, "rb") as f:
            prev = b""
            off = 0
            while True:
                buf = f.read(CHUNK)
                if not buf:
                    break
                data = prev + buf
                for k in KW:
                    i = data.find(k)
                    while i >= 0:
                        hits.append((os.path.basename(p), off - len(prev) + i, k.decode()))
                        i = data.find(k, i + 1)
                prev = data[-OV:]
                off += len(buf)
        done += os.path.getsize(p)
    print("[%s] 文件 %d, %.2f GB, 耗时 %.1fs, 命中 %d" % (
        label, len(paths), total / 2**30, time.time() - t0, len(hits)), flush=True)
    return hits


def main():
    all_hits = []
    for d, pat in TARGETS:
        fs = sorted(glob.glob(os.path.join(d, pat)))
        if fs:
            all_hits += scan(fs, os.path.basename(d))
    print("\n=== 汇总 ===")
    for h in all_hits[:60]:
        print("  %-50s @%d  %s" % h)
    with open(r"D:\Carol-start\_rea\_ifix_hits.txt", "w", encoding="utf-8") as fo:
        for h in all_hits:
            fo.write("%s\t%d\t%s\n" % h)


if __name__ == "__main__":
    main()
