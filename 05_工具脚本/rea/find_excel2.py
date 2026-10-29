# -*- coding: utf-8 -*-
"""直接探测 editor_compressed/data 下哪些包是明文 UnityFS"""
import os, hashlib, struct

D = r"D:\BH3\7.0\runtime\web\asset_bundle\overseas01\1.1\data\editor_compressed\data"

def probe():
    names = sorted(os.listdir(D))
    plain = []
    magics = {}
    for n in names:
        p = os.path.join(D, n)
        if not os.path.isfile(p):
            continue
        sz = os.path.getsize(p)
        with open(p, "rb") as f:
            h = f.read(0x400)
        tag = None
        if h.startswith(b"UnityFS"):
            tag = "PLAIN@0"
        else:
            i = h.find(b"UnityFS")
            if i >= 0:
                tag = "PLAIN@%d" % i
        if tag:
            plain.append((n, sz, tag))
        m = h[:8]
        magics[m] = magics.get(m, 0) + 1
    print("文件数:", len(names))
    print("明文命中:", len(plain))
    for n, sz, t in plain:
        print("  %-50s %10d  %s" % (n, sz, t))
    print("\n前 8 字节分布 top10:")
    for k, v in sorted(magics.items(), key=lambda x: -x[1])[:10]:
        print("  cnt=%-5d %s" % (v, k.hex()))

if __name__ == "__main__":
    probe()
