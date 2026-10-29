# -*- coding: utf-8 -*-
"""扫描热更资源目录，确认 WorldMapUIManager_V2 prefab 是否在其中。

如果命中，说明客户端用的是热更版本，改 Asb/pc 里的 bundle 永远无效。
"""
import os, sys, glob, struct
sys.path.insert(0, r"D:\Carol-start\_rea")
from lz4fast import lz4_decode_limit

ROOTS = [
    r"D:\BH3\7.0\runtime\web\asset_bundle\overseas01\1.1\data\editor_compressed",
    r"D:\BH3\7.0\runtime\web\asset_bundle\overseas01\1.1\event\editor_compressed",
    r"D:\BH3\7.0\runtime\web\asset_bundle\overseas01\1.1\ai\editor_compressed",
]
PATS = [b"WorldMapUIManager_V2", b"MonoWorldMapChallengePanel", b"MapPanel0",
        b"MonoWorldMapEntryContainerBase", b"Task_1/Cover", b"EmptyFlag1"]


def try_lz4(raw):
    """尝试多个起点做 LZ4 解压，返回能解出的片段。"""
    out = bytearray()
    for off in range(0, min(len(raw), 2048)):
        try:
            dec, _ = lz4_decode_limit(raw[off:off + (1 << 20)], 1 << 20)
        except Exception:
            continue
        if len(dec) > 8192 and (b"WorldMap" in dec or b"Mono" in dec or b"CAB-" in dec):
            out += dec
    return bytes(out)


def main():
    files = []
    for r in ROOTS:
        files += glob.glob(os.path.join(r, "**", "*"), recursive=True)
    files = [f for f in files if os.path.isfile(f)]
    print("待扫文件 %d 个" % len(files))
    hit = 0
    for idx, p in enumerate(files):
        raw = open(p, "rb").read()
        found = [pat.decode() for pat in PATS if raw.count(pat)]
        if not found:
            dec = try_lz4(raw)
            found = [pat.decode() + "(lz4)" for pat in PATS if dec.count(pat)]
        if found:
            print("  HIT %s  %d B  %s" % (p, len(raw), ",".join(found)))
            hit += 1
        if (idx + 1) % 200 == 0:
            print("  ... %d/%d" % (idx + 1, len(files)))
    print()
    print("命中 %d 个" % hit)


if __name__ == "__main__":
    main()
