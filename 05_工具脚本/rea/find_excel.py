# -*- coding: utf-8 -*-
"""在 editor_compressed/data 下找出 17 个明文 UnityFS 包，并定位 excel_output"""
import os, sys, struct, hashlib

D = r"D:\BH3\7.0\runtime\web\asset_bundle\overseas01\1.1\data\editor_compressed\data"

# 已知明文签名：前 0x30 字节（17 个文件完全相同）
KNOWN = None

def scan():
    files = []
    for n in sorted(os.listdir(D)):
        p = os.path.join(D, n)
        if not os.path.isfile(p):
            continue
        files.append((n, p))
    print("总文件数:", len(files))

    # 先统计前 0x30 字节的指纹分布
    from collections import Counter
    c = Counter()
    hdr = {}
    for n, p in files:
        try:
            with open(p, "rb") as f:
                h = f.read(0x30)
        except Exception as e:
            continue
        if len(h) < 0x30:
            continue
        k = h
        c[k] += 1
        hdr.setdefault(k, []).append((n, p))

    print("\n前 0x30 字节指纹种类:", len(c))
    for k, v in c.most_common(10):
        print("  cnt=%-5d md5=%s" % (v, hashlib.md5(k).hexdigest()[:16]))

    return files, c, hdr


if __name__ == "__main__":
    scan()
