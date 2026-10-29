"""把 Cover_Title7 换成「迪拉克之海」，且 **bundle 结构一字节不动**。

与 make_dirac.py 的区别：
  * 纹理尺寸保持 204x56（UI 节点的 rect 是 260x56，uGUI 会把图拉伸回 260x56）
  * payload 长度不变 -> block usize 不变 -> blocksInfo 字节不变 -> 头部不变
  * 只把 block3/block4 用 compress_exact 压回**原来的 csize**
  => 除「压缩块里的不透明字节」外，整个 bundle 与原文件完全一致，
     客户端既不会触发 size 校验，也不会因包头/块表异常而加载失败。
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmvkit as K
import repack as R

import numpy as np
from PIL import Image

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
TMP = r"D:/BH3/7.0/_ext/tmp"

SRC_FN = "10d8f3adca3f6d9c0c321cbcf89c72b0.wmv"
SRC_OFF = 31806037
TGT_FN = "0a95a3510bffb1a31fdef2cae36e8783.wmv"
TGT_BIDX = 848
TEX = "Cover_Title7"


def rs(d, p):
    n = struct.unpack_from("<i", d, p)[0]
    if n < 0 or n > 4096 or p + 4 + n > len(d):
        return None, p
    return d[p + 4:p + 4 + n], (p + 4 + n + 3) & ~3


def find_bundle(data, off):
    i = data.find(b"UnityFS\0")
    while 0 <= i <= off:
        b = K.try_bundle(data, i)
        if b and b["start"] <= off < b["start"] + b["total"]:
            return b
        i = data.find(b"UnityFS\0", i + 1)
    return None


def texs(data, b):
    pl = K.bundle_payload(data, b)
    cab = [nd for nd in b["nodes"] if not nd["path"].endswith(".resS")][0]
    res = [nd for nd in b["nodes"] if nd["path"].endswith(".resS")][0]
    seg = pl[cab["offset"]:cab["offset"] + cab["size"]]
    h = K.sf_parse(seg)
    out = {}
    for o in h["objects"]:
        if o["name"] != "Texture2D":
            continue
        d = K.sf_objdata(h, seg, o)
        s, q = rs(d, 0)
        if s is None:
            continue
        wp = (q + 4 + 1 + 3) & ~3
        w, hh = struct.unpack_from("<ii", d, wp)
        cis = struct.unpack_from("<i", d, wp + 8)[0]
        fmt = struct.unpack_from("<i", d, wp + 12)[0]
        q2 = d.find(b"archive:/")
        off = struct.unpack_from("<I", d, q2 - 12)[0] if q2 > 0 else None
        out[s.decode("utf-8", "replace")] = dict(w=w, h=hh, cis=cis, fmt=fmt, off=off)
    return out, res, pl


# ---- 1. 源图（260x56 迪拉克之海）
sd = open(os.path.join(BASE, SRC_FN), 'rb').read()
sb = find_bundle(sd, SRC_OFF)
st, sres, spl = texs(sd, sb)
x = st["Cover_Title8"]
raw = spl[sres["offset"] + x["off"]: sres["offset"] + x["off"] + x["cis"]]
img = Image.frombytes("RGBA", (x["w"], x["h"]), raw).transpose(Image.FLIP_TOP_BOTTOM)
print("源 Cover_Title8 %dx%d" % img.size)

# ---- 2. 目标 bundle
data, bs = R.read_file(os.path.join(BASE, TGT_FN))
b = bs[TGT_BIDX]
tt, tres, pl = texs(data, b)
t = tt[TEX]
print("目标 %s %dx%d fmt=%d cis=%d off=%d" % (TEX, t["w"], t["h"], t["fmt"], t["cis"], t["off"]))
assert t["fmt"] == 4 and t["w"] * t["h"] * 4 == t["cis"]

# ---- 3. NEAREST 缩放到目标尺寸（保住硬边，压缩率才够）
new = img.resize((t["w"], t["h"]), Image.NEAREST)
buf = np.array(new)[::-1].tobytes()          # Unity 底部朝上
assert len(buf) == t["cis"]

pl2 = bytearray(pl)
ins = tres["offset"] + t["off"]
pl2[ins:ins + t["cis"]] = buf

# ---- 4. 等长重打包（只动压缩块，块表/包头不变）
nb, info = R.repack(data, b, bytes(pl2), keep_size=True, verbose=True)
assert nb is not None, info
out = data[:b["start"]] + nb + data[b["start"] + b["total"]:]
print("repack:", {k: info[k] for k in ("bi_len", "new_bi_len", "total", "new_total")})
assert len(out) == len(data), "文件长度变了"

# ---- 5. 结构等价性断言
b2 = K.try_bundle(out, b["start"])
assert b2["total"] == b["total"] and b2["bi_len"] == b["bi_len"], "块表长度变了"
assert out[b["start"]:b["start"] + 54] == data[b["start"]:b["start"] + 54], "头部变了"
assert R.bi_body(out, b2) == R.bi_body(data, b), "blocksInfo 内容变了"
assert [x[1] for x in b2["blocks"]] == [x[1] for x in b["blocks"]], "csize 变了"
assert [x[0] for x in b2["blocks"]] == [x[0] for x in b["blocks"]], "usize 变了"
print("结构等价性: 头部/块表/块尺寸 全部与原文件一致")

pl3 = K.bundle_payload(out, b2)
assert pl3[ins:ins + t["cis"]] == buf, "像素回读不一致"
print("像素回读一致")

_, bs2 = K.walk(data=out)
bad = [i for i, z in enumerate(bs2) if not z["ok"]]
print("全局复检: bundles=%d 失败=%d" % (len(bs2), len(bad)))

dst = os.path.join(TMP, TGT_FN + ".fit")
open(dst, 'wb').write(out)
print("已写出:", dst, len(out), "bytes")
