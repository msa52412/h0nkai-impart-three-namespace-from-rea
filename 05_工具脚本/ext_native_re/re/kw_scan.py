"""在 440 个 .wmv 的【压缩态原始字节】里搜关键字。
LZ4 的字面量是原样存储，所以 ASCII 字符串通常能在压缩流里直接命中。
"""
import glob
import os
import sys

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"

KEYS = [b"WorldMap", b"worldmap", b"WORLDMAP",
        b"Abyss", b"abyss", b"Dirac", b"dirac",
        b"Quantum", b"Superstring", b"superstring",
        b"Cover_", b"cover_", b"TaskPanel", b"Task_",
        b"Ultra", b"Challenge", b"ChallengeGroup"]
KEYS = [k for k in dict.fromkeys(KEYS)]


def main():
    fs = sorted(glob.glob(os.path.join(BASE, "*.wmv")), key=os.path.getsize)
    hits = {}
    for i, f in enumerate(fs):
        d = open(f, 'rb').read()
        found = []
        for k in KEYS:
            c = d.count(k)
            if c:
                found.append((k.decode(), c))
        if found:
            hits[os.path.basename(f)] = found
        if i % 40 == 0:
            print("... %d/%d 命中文件=%d" % (i, len(fs), len(hits)), flush=True)
    print()
    print("=== 命中情况 ===")
    from collections import Counter
    per = Counter()
    for n, found in hits.items():
        for k, c in found:
            per[k] += 1
    print("关键字 -> 命中文件数:", per.most_common())
    print()
    for n, found in sorted(hits.items(), key=lambda x: -sum(c for _, c in x[1]))[:25]:
        print("%-42s %s" % (n, found))


if __name__ == "__main__":
    main()
