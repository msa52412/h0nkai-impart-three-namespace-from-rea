"""repack 自测：改 payload -> 重打包 -> 全局复检 -> payload 一致性。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmvkit as K
import repack as R

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
CASES = [
    ("2b869220f02125f5f74351dc3738788e.wmv", [0, 1]),
    ("426491342dde4dcdb8afbb3b895051e6.wmv", [0]),
    ("0a95a3510bffb1a31fdef2cae36e8783.wmv", [0, 848]),
]

for fn, idxs in CASES:
    path = os.path.join(BASE, fn)
    data, bs = R.read_file(path)
    print("=" * 96)
    print("%s  %d bytes bundles=%d" % (fn, len(data), len(bs)))
    for bi in idxs:
        b = bs[bi]
        if not b["ok"]:
            print("  bundle#%d 解析失败，跳过" % bi)
            continue
        pl = K.bundle_payload(data, b)
        # 改 3 个字节（分散在 payload 不同位置）
        pn = bytearray(pl)
        spots = [len(pl) // 4, len(pl) // 2, len(pl) - 32]
        for s in spots:
            pn[s] ^= 0xA5
        pn = bytes(pn)
        nb, info = R.repack(data, b, pn, verbose=True)
        if nb is None:
            print("  bundle#%d 失败: %s" % (bi, info))
            continue
        print("  bundle#%d  total %d -> %d  bi_len %d -> %d  %s" %
              (bi, info["total"], info["new_total"], info["bi_len"],
               info["new_bi_len"], "size keep"))
        # 校验新 bundle 自身
        b2 = K.try_bundle(nb + b"UnityFS\0", 0)
        if not b2:
            print("    !! 新 bundle 无法自解析")
            continue
        pl2 = K.bundle_payload(nb, b2)
        print("    新 bundle: total=%d blocks=%d nodes=%d payload=%d 内容一致=%s" %
              (b2["total"], b2["block_count"], b2["node_count"], len(pl2),
               pl2 == pn))
        # 把头部的 total 字段也核对一遍
        print("    head.total 解码 = %d (应为 %d)" % (R.dec_total(nb[:0x36]), len(nb)))
        # 文件级替换 + 全局复检
        out = data[:b["start"]] + nb + data[b["start"] + b["total"]:]
        _, bs2 = K.walk(data=out)
        bad = [x for x in bs2 if not x["ok"]]
        print("    文件: %d -> %d bytes  bundles=%d  失败=%d" %
              (len(data), len(out), len(bs2), len(bad)))
        if bad:
            for x in bad[:3]:
                print("      坏 bundle @%d 剩余 %d" % (x["start"], x["rest"]))
