"""swap_title —— 把世界地图 Task_3 的标题图换成指定封面图（可反复切换、可回退）。

用法：
  python swap_title.py dirac            # 换成「迪拉克之海」(默认直接写入游戏目录)
  python swap_title.py superstring      # 换回「超弦空间」
  python swap_title.py openabyss        # 换回原始的「开放深渊」
  python swap_title.py dirac --dry      # 只生成到 _ext/tmp，不动游戏目录

原理（已验证）：
  * Cover_Title7 所在 UI 节点的 sizeDelta = 260x56，所以纹理按原生 260x56 放进去即 1:1
  * resS 内插入/删除字节后，后续纹理的 m_StreamData.offset 同步平移
  * blocksInfo / block usize / 头部 total 由 repack 重算
"""
import os
import shutil
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmvkit as K
import repack as R

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
TMP = r"D:/BH3/7.0/_ext/tmp"
BACKUP = r"D:/BH3/7.0/_ext/backup"
ORIG = os.path.join(BACKUP, "0a95a3510bffb1a31fdef2cae36e8783.wmv.orig")

TGT_FN = "0a95a3510bffb1a31fdef2cae36e8783.wmv"
TGT_BIDX = 848
TGT_TEX = "Cover_Title7"

# 名字 -> (文件, bundle 起始偏移, 该 bundle 内纹理名)
SOURCES = {
    "dirac":       ("10d8f3adca3f6d9c0c321cbcf89c72b0.wmv", 31806037, "Cover_Title8"),   # 迪拉克之海 260x56
    "superstring": ("10d8f3adca3f6d9c0c321cbcf89c72b0.wmv", 31797069, "Cover_Title12"),  # 超弦空间 204x56
    "deeparchive": ("f5ee331203a685423e94d1bec0bbdb4e.wmv", 47627739, "Cover_Title5"),   # 深层档案 204x56
    "rolechallenge": ("f5ee331203a685423e94d1bec0bbdb4e.wmv", 47636871, "Cover_Title9"), # 角色挑战 204x56
    "challengeway": ("5ca670844a1a73364a8ac9d00bfab2c0.wmv", 19829852, "Cover_Title9"),  # 挑战之路 204x56
    "diracen":     ("6d45a4650aab5060c5c31b5431e37bc8.wmv", 749864, "Cover_Title8"),     # Dirac Sea 220x56 DXT5
}


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
        wp = (q + 4 + 1 + 3) & ~3
        w, hh = struct.unpack_from("<ii", d, wp)
        cis = struct.unpack_from("<i", d, wp + 8)[0]
        fmt = struct.unpack_from("<i", d, wp + 12)[0]
        q2 = d.find(b"archive:/")
        off = struct.unpack_from("<I", d, q2 - 12)[0] if q2 > 0 else None
        out.append(dict(name=s.decode("utf-8", "replace"), w=w, h=hh, cis=cis, fmt=fmt,
                        off=off, p_w=base + wp, p_cis=base + wp + 8,
                        p_off=(base + q2 - 12) if q2 > 0 else None))
    return out, res, pl


def grab_source(key):
    fn, off, tex = SOURCES[key]
    data = open(os.path.join(BASE, fn), 'rb').read()
    sb = find_bundle(data, off)
    if not sb:
        raise SystemExit("源 bundle 定位失败: %s@%d" % (fn, off))
    te, sres, spl = tex_entries(data, sb)
    hit = [x for x in te if x["name"] == tex]
    if not hit:
        raise SystemExit("源里找不到 %s" % tex)
    x = hit[0]
    px = spl[sres["offset"] + x["off"]: sres["offset"] + x["off"] + x["cis"]]
    if x["fmt"] != 4 or len(px) != x["w"] * x["h"] * 4:
        raise SystemExit("源纹理不是 RGBA32/直读: fmt=%d" % x["fmt"])
    return x["w"], x["h"], px


def build(base_path, key):
    NW, NH, px = grab_source(key)
    data, bs = R.read_file(base_path)
    b = bs[TGT_BIDX]
    te, res, pl = tex_entries(data, b)
    t = [x for x in te if x["name"] == TGT_TEX][0]
    if t["fmt"] != 4 or t["h"] != NH:
        raise SystemExit("目标格式/高度不兼容: fmt=%d %dx%d" % (t["fmt"], t["w"], t["h"]))
    OCIS = t["cis"]
    delta = len(px) - OCIS
    cur = pl[res["offset"] + t["off"]:res["offset"] + t["off"] + OCIS]
    if delta == 0 and NW == t["w"] and px == cur:
        return data, None, "源与目标像素完全一致，无需改动"

    pl2 = bytearray(pl)
    struct.pack_into("<i", pl2, t["p_w"], NW)
    struct.pack_into("<i", pl2, t["p_cis"], len(px))
    for x in te:
        if x is t or x["off"] is None:
            continue
        if x["off"] >= t["off"] + OCIS:
            struct.pack_into("<I", pl2, x["p_off"], x["off"] + delta)

    ins = res["offset"] + t["off"]
    tail = res["offset"] + t["off"] + OCIS
    new_pl = bytes(pl2[:ins]) + px + bytes(pl2[tail:])

    blocks = [list(x) for x in b["blocks"]]
    d2 = len(new_pl) - len(pl)
    if d2:
        blocks[-1][0] += d2
    if sum(x[0] for x in blocks) != len(new_pl):
        raise SystemExit("block 合计与 payload 不符")
    _, nodes0, _ = R.bi_parse(R.bi_body(data, b))
    nodes = [[o, s + (d2 if (p.endswith(".resS") and o == res["offset"]) else 0), f, p]
             for (o, s, f, p) in nodes0]

    nb, info = R.repack_keep_total(data, b, new_pl, blocks, nodes, verbose=True)
    if nb is None:
        raise SystemExit("重打包失败: %s" % info)
    out = data[:b["start"]] + nb + data[b["start"] + b["total"]:]
    assert len(out) == len(data), "文件字节数变了：%d -> %d" % (len(data), len(out))
    _, bs2 = K.walk(data=out)
    bad = [i for i, x in enumerate(bs2) if not x["ok"]]
    return out, (info, bad, NW, NH), "%s %dx%d  cis %d -> %d  bundle total %d(不变)  文件 %d bytes(不变)  失败包 %d" % (
        key, NW, NH, OCIS, len(px), b["total"], len(out), len(bad))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    dry = "--dry" in sys.argv
    key = args[0] if args else "dirac"
    if key not in SOURCES:
        raise SystemExit("可用: %s" % ", ".join(SOURCES))
    apply_ = not dry
    src = ORIG if (apply_ and os.path.exists(ORIG)) else os.path.join(BASE, TGT_FN)
    if key == "openabyss":
        src = ORIG
        if not os.path.exists(src):
            raise SystemExit("没有原始备份: %s" % ORIG)
        if apply_:
            shutil.copy2(src, os.path.join(BASE, TGT_FN))
            print("已还原原始文件（开放深渊）")
        return
    out, info, msg = build(src, key)
    print(msg)
    dst = os.path.join(TMP, TGT_FN + ".swap")
    if out is not None:
        open(dst, 'wb').write(out)
        print("生成:", dst)
    if apply_:
        if not os.path.exists(ORIG):
            os.makedirs(BACKUP, exist_ok=True)
            shutil.copy2(os.path.join(BASE, TGT_FN), ORIG)
            print("已备份原始:", ORIG)
        shutil.copy2(dst, os.path.join(BASE, TGT_FN))
        print("已写入游戏目录")


if __name__ == "__main__":
    main()
