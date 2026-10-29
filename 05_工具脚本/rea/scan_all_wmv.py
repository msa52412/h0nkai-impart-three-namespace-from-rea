# -*- coding: utf-8 -*-
"""全盘扫描 Asb/pc 下所有 wmv，找出 SF.fileSize=412587 且含 WorldMapUIManager_V2 的 bundle。

依据：目标 bundle #848 的 nodes[0].size = 412587（SerializedFile 大小），
这个尺寸是 prefab 的特征，用来快速筛选，避免全量解压。
"""
import os, sys, glob, time, struct
sys.path.insert(0, r"D:\BH3\7.0\_ext\re")
import wmvkit

ASB = r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc"
TARGET_SF = 412587
PATS = [b"WorldMapUIManager_V2", b"MonoWorldMapChallengePanel"]


def main():
    files = sorted(glob.glob(os.path.join(ASB, "*.wmv")))
    print("扫描 %d 个 wmv" % len(files))
    t0 = time.time()
    cand = []
    for idx, p in enumerate(files):
        try:
            data = open(p, "rb").read()
        except Exception as e:
            print("  读取失败 %s %s" % (p, e))
            continue
        try:
            _, bs = wmvkit.walk(data=data)
        except Exception as e:
            print("  walk 失败 %s %s" % (os.path.basename(p), e))
            continue
        for i, b in enumerate(bs):
            nodes = b.get("nodes") or []
            if not nodes:
                continue
            if abs(nodes[0].get("size", 0) - TARGET_SF) > 4096:
                continue
            try:
                pl = wmvkit.bundle_payload(data, b)
            except Exception:
                continue
            hits = [pat.decode() for pat in PATS if pl.count(pat)]
            cand.append((p, i, len(pl), hits))
            print("  CAND %s #%d payload=%d %s" % (os.path.basename(p), i, len(pl), hits or "(无命中)"))
        if (idx + 1) % 50 == 0:
            print("  ... %d/%d %.1fs" % (idx + 1, len(files), time.time() - t0))
    print()
    print("候选 %d 个，用时 %.1fs" % (len(cand), time.time() - t0))
    for p, i, n, h in cand:
        print("  %s #%d %d %s" % (os.path.basename(p), i, n, h))


if __name__ == "__main__":
    main()
