"""把 Cover_Title7（204x56「开放深渊」）换成原生 260x56「迪拉克之海」。

要点：
  * 目标纹理所在 Image 的 rect 是 260x56，所以纹理也做成 260x56 -> 1:1 显示
  * resS 在 101156 处插入 (58240-45696)=12544 字节，其后 4 张纹理 m_StreamData.offset 全部 +12544
  * 由于插入点在 resS 内，resS 尾部自然延伸到 payload 尾部，追加的 12544 字节正好是最后一个 block 的增长
  * 只改字节，不新增/删除对象
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmvkit as K
import repack as R

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
OUTDIR = r"D:/BH3/7.0/_ext/tmp"

SRC_FN = "10d8f3adca3f6d9c0c321cbcf89c72b0.wmv"
SRC_OFF = 31806037          # 含 Cover_Title8 260x56「迪拉克之海」
TGT_FN = "0a95a3510bffb1a31fdef2cae36e8783.wmv"
TGT_BIDX = 848

TEX_NAME = "Cover_Title7"


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


def tex_entries(data, b):
    """返回 [{name,w,h,cis,fmt,off_path_pos,cab_abs,...}]，位置均为 bundle payload 内绝对偏移。"""
    pl = K.bundle_payload(data, b)
    cab = [nd for nd in b["nodes"] if not nd["path"].endswith(".resS")][0]
    res = [nd for nd in b["nodes"] if nd["path"].endswith(".resS")][0]
    seg = pl[cab["offset"]:cab["offset"] + cab["size"]]
    h = K.sf_parse(seg)
    out = []
    for o in h["objects"]:
        if o["name"] != "Texture2D":
            continue
        base = cab["offset"] + h["data_offset"] + o["byte_start"]
        d = K.sf_objdata(h, seg, o)
        s, q = rs(d, 0)
        if s is None:
            continue
        name = s.decode("utf-8", "replace")
        wp = (q + 4 + 1 + 3) & ~3
        w, hh = struct.unpack_from("<ii", d, wp)
        cis = struct.unpack_from("<i", d, wp + 8)[0]
        fmt = struct.unpack_from("<i", d, wp + 12)[0]
        q2 = d.find(b"archive:/")
        off = struct.unpack_from("<I", d, q2 - 12)[0] if q2 > 0 else None
        out.append(dict(name=name, w=w, h=hh, cis=cis, fmt=fmt, off=off,
                        p_w=base + wp, p_h=base + wp + 4, p_cis=base + wp + 8,
                        p_off=(base + q2 - 12) if q2 > 0 else None,
                        cab=base, res=res, pl=pl))
    return out, h, cab, res, pl


# ---------------------------------------------------------------- 1. 取源像素
src_data = open(os.path.join(BASE, SRC_FN), 'rb').read()
sb = find_bundle(src_data, SRC_OFF)
assert sb, "源 bundle 定位失败"
se, _, scab, sres, spl = tex_entries(src_data, sb)
d8 = [t for t in se if t["name"] == "Cover_Title8"]
assert d8, "源里找不到 Cover_Title8"
d8 = d8[0]
NW, NH = d8["w"], d8["h"]
new_px = spl[sres["offset"] + d8["off"]: sres["offset"] + d8["off"] + d8["cis"]]
print("源 %s %dx%d fmt=%d cis=%d 实际像素=%d 字节" %
      (d8["name"], NW, NH, d8["fmt"], d8["cis"], len(new_px)))
assert len(new_px) == NW * NH * 4 and len(new_px) == d8["cis"], "源像素长度不符"

# ---------------------------------------------------------------- 2. 目标定位
tgt_path = os.path.join(BASE, TGT_FN)
data, bs = R.read_file(tgt_path)
b = bs[TGT_BIDX]
te, h, cab, res, pl = tex_entries(data, b)
print("目标 bundle@%d total=%d payload=%d resS off=%d size=%d" %
      (b["start"], b["total"], len(pl), res["offset"], res["size"]))

t = [x for x in te if x["name"] == TEX_NAME]
assert len(t) == 1, "目标纹理不唯一: %d" % len(t)
t = t[0]
OW, OH, OCIS = t["w"], t["h"], t["cis"]
print("目标 %s %dx%d fmt=%d cis=%d off=%d  (对象@%d)" %
      (t["name"], OW, OH, t["fmt"], OCIS, t["off"], t["cab"]))
assert t["fmt"] == 4 and OH == NH, "格式/高度不符，无法直接换"
delta = len(new_px) - OCIS
assert delta > 0
print("尺寸变化: %d -> %d (%+d)" % (OCIS, len(new_px), delta))

# ---------------------------------------------------------------- 3. 改字段
pl2 = bytearray(pl)
struct.pack_into("<i", pl2, t["p_w"], NW)
struct.pack_into("<i", pl2, t["p_cis"], len(new_px))
print("已改 %s: w %d->%d  cis %d->%d" % (TEX_NAME, OW, NW, OCIS, len(new_px)))

shifted = []
for x in te:
    if x is t or x["off"] is None:
        continue
    if x["off"] >= t["off"] + OCIS:
        old = x["off"]
        struct.pack_into("<I", pl2, x["p_off"], old + delta)
        shifted.append((x["name"], old, old + delta))
print("后续纹理偏移 +%d：" % delta)
for nm, a, c in sorted(shifted, key=lambda z: z[1]):
    print("   %-18s %d -> %d" % (nm, a, c))

# 校验：resS 内像素区间必须首尾相接
bounds = sorted([(x["off"], x["off"] + x["cis"], x["name"]) for x in te if x["off"] is not None])
bnd = []
for s0, e0, nm in bounds:
    if nm == TEX_NAME:
        e0 = s0 + len(new_px)
    elif any(nm == s[0] for s in shifted):
        sh = [s for s in shifted if s[0] == nm][0]
        s0, e0 = sh[2], sh[2] + e0 - s0
    bnd.append((s0, e0, nm))
bnd.sort()
cur = 0
ok = True
for s0, e0, nm in bnd:
    if s0 != cur:
        print("   !! 空隙/重叠 %s: 期望 %d 实际 %d" % (nm, cur, s0))
        ok = False
    cur = e0
print("resS 布局连续: %s  结束=%d  期望=%d" % (ok, cur, res["size"] + delta))
assert ok and cur == res["size"] + delta

# ---------------------------------------------------------------- 4. 拼新 payload
ins = res["offset"] + t["off"]
tail = res["offset"] + t["off"] + OCIS
new_pl = bytes(pl2[:ins]) + new_px + bytes(pl2[tail:])
print("新 payload: %d -> %d" % (len(pl), len(new_pl)))
assert len(new_pl) == len(pl) + delta

# 最后一个 block 扩容（插入点之后的尾部自然延伸）
blocks = [list(x) for x in b["blocks"]]
blocks[-1][0] += delta
assert sum(x[0] for x in blocks) == len(new_pl), "block usize 合计与 payload 不符"
_, nodes0, _ = R.bi_parse(R.bi_body(data, b))
nodes = []
for off_, size_, fl, pth in nodes0:
    if pth.endswith(".resS") and off_ == res["offset"]:
        size_ += delta
    nodes.append([off_, size_, fl, pth])
print("blocks:", blocks)
print("nodes :", nodes)

# ---------------------------------------------------------------- 5. 重打包
nb, info = R.repack(data, b, new_pl, keep_size=False, verbose=True,
                    blocks_override=blocks, nodes_override=nodes)
assert nb is not None, info
print("repack:", {k: info[k] for k in ("bi_len", "new_bi_len", "total", "new_total")})
out = data[:b["start"]] + nb + data[b["start"] + b["total"]:]
_, bs2 = K.walk(data=out)
bad = [i for i, x in enumerate(bs2) if not x["ok"]]
print("全局复检: bundles=%d 失败=%d" % (len(bs2), len(bad)))

# ---------------------------------------------------------------- 6. 回读校验
b2 = bs2[TGT_BIDX]
pl3 = K.bundle_payload(out, b2)
assert pl3[ins:ins + len(new_px)] == new_px, "插入区内容不一致"
te2, _, _, res2, _ = tex_entries(out, b2)
t2 = [x for x in te2 if x["name"] == TEX_NAME][0]
print("回读 %s: %dx%d cis=%d off=%d" % (t2["name"], t2["w"], t2["h"], t2["cis"], t2["off"]))
assert (t2["w"], t2["h"], t2["cis"]) == (NW, NH, len(new_px))

dst = os.path.join(OUTDIR, TGT_FN + ".dirac")
open(dst, 'wb').write(out)
print("\n已写出: %s  (%d -> %d bytes)" % (dst, len(data), len(out)))
