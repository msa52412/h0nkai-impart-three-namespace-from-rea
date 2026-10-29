# -*- coding: utf-8 -*-
"""扫描全部 .wmv（16GB）裸字节搜索 WorldMap 预制体特征串。

LZ4 字面量会原样保留 ASCII 串，所以裸搜对大部分字符串有效
（少数被 match 引用切断的串会漏，例如 WorldMapUIManager）。
"""
import glob, os, sys, time

D = r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc"
KEYS = [b"Task_1", b"Task_2", b"Task_3", b"Task_4", b"Task_5",
        b"Task_6", b"Task_7", b"Task_8", b"Task_9",
        b"MapPanel", b"TypeTab", b"Canvas2D", b"EntryContainer",
        b"OWEndless", b"Endless"]

CHUNK = 8 * 1024 * 1024
OVER = 64


def scan(path, keys):
    hits = {k: 0 for k in keys}
    size = os.path.getsize(path)
    tail = b""
    with open(path, "rb") as f:
        while True:
            buf = f.read(CHUNK)
            if not buf:
                break
            data = tail + buf
            for k in keys:
                c = data.count(k)
                if c:
                    hits[k] += c
            tail = data[-OVER:]
    return hits, size


def main():
    files = sorted(glob.glob(os.path.join(D, "*.wmv")))
    total = sum(os.path.getsize(f) for f in files)
    print("扫描 %d 个 wmv，共 %.2f GB" % (len(files), total / 2 ** 30))
    t0 = time.time()
    found = []
    for i, p in enumerate(files):
        hits, size = scan(p, KEYS)
        if any(hits.values()):
            nz = {k.decode(): v for k, v in hits.items() if v}
            found.append((os.path.basename(p), size, nz))
            print("[%d/%d] %s  %d B  %s" % (i + 1, len(files), os.path.basename(p), size, nz))
        if (i + 1) % 50 == 0:
            el = time.time() - t0
            print("  ... %d/%d  %.0fs  已读 %.1f GB"
                  % (i + 1, len(files), el, sum(os.path.getsize(f) for f in files[:i + 1]) / 2 ** 30))
    print()
    print("=== 命中文件 %d 个，耗时 %.1fs ===" % (len(found), time.time() - t0))
    for n, s, nz in found:
        print("  %s  %d B  %s" % (n, s, nz))


if __name__ == "__main__":
    main()
