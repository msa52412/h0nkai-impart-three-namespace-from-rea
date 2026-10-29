# -*- coding: utf-8 -*-
"""扫描热更缓存 Data/data/*.unity3d，找出含目标 prefab 的那个。

Data/data 里的文件名格式是 {uint32}_{SHA1}，是 miHoYo 下载缓存。
如果挑战面板 prefab 在这里有更新版本，游戏会优先用它，改 Asb/pc 就无效。
"""
import os, sys, struct, glob
sys.path.insert(0, r"D:\Carol-start\_rea")
from lz4fast import lz4_decode_limit

DIR = r"C:\Users\Administrator\AppData\LocalLow\miHoYo\Honkai Impact 3\Data\data"
PATS = [b"WorldMapUIManager_V2", b"MonoWorldMapChallengePanel", b"MapPanel0",
        b"MonoWorldMapEntryContainerBase", b"Task_1", b"EmptyFlag1"]


def try_unityfs(raw):
    """解出 UnityFS 里每个 LZ4 block 的前若干字节，返回拼接文本片段。"""
    out = bytearray()
    if not raw.startswith(b"UnityFS\x00"):
        return bytes(out)
    # 头部是可变长字符串，直接从头扫 LZ4 块标志位不可靠；
    # 改为暴力：在文件里找 LZ4 块头（miHoYo 变体通常是 [u32 csize][u32 usize] 或纯 raw 块）
    # 这里用最朴素的办法——把整个文件按 4 种可能偏移做 lz4_decode_limit 试探
    for off in range(0, min(len(raw), 4096)):
        try:
            dec, _ = lz4_decode_limit(raw[off:off + (1 << 20)], 1 << 18)
        except Exception:
            continue
        if len(dec) >= 4096 and (b"WorldMap" in dec or b"Mono" in dec or b"CAB-" in dec or b"2017.4" in dec):
            out += dec
    return bytes(out)


def main():
    files = sorted(glob.glob(os.path.join(DIR, "*.unity3d")))
    print("扫描 %d 个 unity3d" % len(files))
    found = []
    for idx, p in enumerate(files):
        raw = open(p, "rb").read()
        hit = []
        # 先直接搜（未压缩的元数据可能明文）
        for pat in PATS:
            if raw.count(pat):
                hit.append(pat.decode())
        if not hit:
            dec = try_unityfs(raw)
            for pat in PATS:
                if dec.count(pat):
                    hit.append(pat.decode() + "(lz4)")
        if hit:
            found.append((p, len(raw), hit))
            print("  [%d/%d] %s  %d B  %s" % (idx + 1, len(files), os.path.basename(p), len(raw), ",".join(hit)))
        if (idx + 1) % 50 == 0:
            print("  ... 已扫 %d" % (idx + 1))
    print()
    print("命中 %d 个文件" % len(found))
    for p, s, h in found:
        print("  %s  %d B  %s" % (os.path.basename(p), s, ",".join(h)))


if __name__ == "__main__":
    main()
