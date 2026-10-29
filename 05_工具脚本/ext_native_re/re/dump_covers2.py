"""按任意偏移定位 bundle（magic 全扫，绕过 walk 中途失败），导出纹理。
新增 DXT1/DXT5(BC1/BC3) 解码，纯 numpy 实现。
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmvkit as K

import numpy as np
from PIL import Image

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
OUT = r"D:/BH3/7.0/_ext/tmp/tex"
os.makedirs(OUT, exist_ok=True)

FMT = {1: "Alpha8", 2: "ARGB4444", 3: "RGB24", 4: "RGBA32", 5: "ARGB32",
       7: "RGB565", 10: "DXT1", 12: "DXT5", 13: "RGBA4444", 14: "BGRA32",
       47: "BC7", 49: "BC6H"}


def rs(b, p):
    n = struct.unpack_from("<i", b, p)[0]
    if n < 0 or n > 4096 or p + 4 + n > len(b):
        return None, p
    return b[p + 4:p + 4 + n], (p + 4 + n + 3) & ~3


def parse_tex(d):
    s, q = rs(d, 0)
    if s is None:
        return None
    name = s.decode("utf-8", "replace")
    p = q
    try:
        p += 4                      # m_ForcedFallbackFormat
        p += 1                      # m_DownscaleFallback
        p = (p + 3) & ~3
        w, h = struct.unpack_from("<ii", d, p); p += 8
        cis = struct.unpack_from("<i", d, p)[0]; p += 4
        tf = struct.unpack_from("<i", d, p)[0]; p += 4
        mip = struct.unpack_from("<i", d, p)[0]; p += 4
    except Exception:
        return None
    q2 = d.find(b"archive:/")
    if q2 < 0:
        return {"name": name, "w": w, "h": h, "fmt": tf, "size": cis, "off": None}
    off, size, plen = struct.unpack_from("<III", d, q2 - 12)
    return {"name": name, "w": w, "h": h, "fmt": tf, "size": cis,
            "mip": mip, "off": off}


# ---------- BC 解码 ----------
def _rgb565(v):
    r = (v >> 11) & 31
    g = (v >> 5) & 63
    b = v & 31
    return np.stack([(r * 255 + 15) // 31, (g * 255 + 31) // 63,
                     (b * 255 + 15) // 31], -1).astype(np.uint8)


def dxt1(data, w, h):
    bw, bh = (w + 3) // 4, (h + 3) // 4
    blk = np.frombuffer(data, dtype=np.uint8, count=bw * bh * 8).reshape(-1, 8)
    c0 = (blk[:, 0].astype(np.uint16) | (blk[:, 1].astype(np.uint16) << 8))
    c1 = (blk[:, 2].astype(np.uint16) | (blk[:, 3].astype(np.uint16) << 8))
    e0 = _rgb565(c0)
    e1 = _rgb565(c1)
    idx = blk[:, 4:8].reshape(-1, 4).astype(np.uint32)
    idx = ((idx[:, 0].astype(np.uint32)) | (idx[:, 1].astype(np.uint32) << 8) |
           (idx[:, 2].astype(np.uint32) << 16) | (idx[:, 3].astype(np.uint32) << 24))
    bits = np.stack([(idx >> (2 * i)) & 3 for i in range(16)], 1)
    a0 = e0.astype(np.int16)
    a1 = e1.astype(np.int16)
    pal = np.zeros((blk.shape[0], 4, 3), np.uint8)
    pal[:, 0] = e0
    pal[:, 1] = e1
    mode_c1_gt = (c0 > c1).astype(bool)
    p2 = ((2 * a0 + a1) // 3).astype(np.uint8)
    p3 = ((a0 + 2 * a1) // 3).astype(np.uint8)
    pal[:, 2] = np.where(mode_c1_gt[:, None], p2, ((a0 + a1) // 2).astype(np.uint8))
    pal[:, 3] = np.where(mode_c1_gt[:, None], p3, 0)
    out = np.zeros((blk.shape[0], 16, 4), np.uint8)
    for i in range(16):
        out[:, i, :3] = np.take_along_axis(
            pal, bits[:, i][:, None, None].repeat(3, 2), 1)[:, 0, :]
    out[:, :, 3] = np.where(
        (bits == 3) & (~mode_c1_gt[:, None]), 0, 255).astype(np.uint8)
    return _assemble(out, bw, bh, w, h)


def dxt5(data, w, h):
    bw, bh = (w + 3) // 4, (h + 3) // 4
    blk = np.frombuffer(data, dtype=np.uint8, count=bw * bh * 16).reshape(-1, 16)
    a0 = blk[:, 0].astype(np.int16)
    a1 = blk[:, 1].astype(np.int16)
    ai = blk[:, 2:8].reshape(-1, 6).astype(np.uint32)
    abits = (ai[:, 0].astype(np.uint64) | (ai[:, 1].astype(np.uint64) << 8) |
             (ai[:, 2].astype(np.uint64) << 16) | (ai[:, 3].astype(np.uint64) << 24) |
             (ai[:, 4].astype(np.uint64) << 32) | (ai[:, 5].astype(np.uint64) << 40))
    bits = np.stack([(abits >> np.uint64(3 * i)) & np.uint64(7)
                     for i in range(16)], 1).astype(np.int16)
    apal = np.zeros((blk.shape[0], 8), np.int16)
    apal[:, 0] = a0
    apal[:, 1] = a1
    gt = a0 > a1
    gg = np.arange(2, 8)
    # a0>a1: 6 个插值 ((7-j)*a0+(j-1)*a1)/7
    gt_vals = np.stack([((7 - j) * a0 + (j - 1) * a1) // 7 for j in gg], 1)
    # a0<=a1: j=2..5 用 ((5-j)*a0+(j-1)*a1)/5，j=6 -> 0，j=7 -> 255
    le_vals = np.stack([((5 - j) * a0 + (j - 1) * a1) // 5 for j in gg], 1)
    le_vals[:, 4] = 0
    le_vals[:, 5] = 255
    apal[:, 2:8] = np.where(gt[:, None], gt_vals, le_vals)
    alpha = np.take_along_axis(apal, bits, 1).astype(np.uint8)

    c0 = (blk[:, 8].astype(np.uint16) | (blk[:, 9].astype(np.uint16) << 8))
    c1 = (blk[:, 10].astype(np.uint16) | (blk[:, 11].astype(np.uint16) << 8))
    e0 = _rgb565(c0)
    e1 = _rgb565(c1)
    ci = blk[:, 12:16].reshape(-1, 4).astype(np.uint32)
    cidx = (ci[:, 0] | (ci[:, 1] << 8) | (ci[:, 2] << 16) | (ci[:, 3] << 24))
    cbits = np.stack([(cidx >> (2 * i)) & 3 for i in range(16)], 1)
    a0c = e0.astype(np.int16)
    a1c = e1.astype(np.int16)
    cpal = np.zeros((blk.shape[0], 4, 3), np.uint8)
    cpal[:, 0] = e0
    cpal[:, 1] = e1
    cpal[:, 2] = ((2 * a0c + a1c) // 3).astype(np.uint8)
    cpal[:, 3] = ((a0c + 2 * a1c) // 3).astype(np.uint8)
    rgb = np.take_along_axis(cpal, cbits[:, :, None], 1)
    out = np.zeros((blk.shape[0], 16, 4), np.uint8)
    out[:, :, :3] = rgb
    out[:, :, 3] = alpha
    return _assemble(out, bw, bh, w, h)


def _assemble(out, bw, bh, w, h):
    img = out.reshape(bh, bw, 4, 4, 4)
    img = img.transpose(0, 2, 1, 3, 4).reshape(bh * 4, bw * 4, 4)
    return Image.fromarray(np.ascontiguousarray(img[:h, :w]), "RGBA")


def to_image(raw, w, h, tf):
    if tf == 4:
        return Image.frombytes("RGBA", (w, h), raw[:w * h * 4])
    if tf == 3:
        return Image.frombytes("RGB", (w, h), raw[:w * h * 3]).convert("RGBA")
    if tf == 5:
        im = Image.frombytes("RGBA", (w, h), raw[:w * h * 4])
        a = im.getchannel("A")
        im.putalpha(im.getchannel("R"))
        r = im.getchannel("A")
        return Image.merge("RGBA", (im.getchannel("G"), im.getchannel("B"), r, a))
    if tf == 14:
        return Image.frombytes("RGBA", (w, h), raw[:w * h * 4])
    if tf == 10:
        return dxt1(raw, w, h)
    if tf == 12:
        return dxt5(raw, w, h)
    return None


def find_bundle(data, off):
    """magic 全扫定位：任何 p 处 data[p:p+8]=='UnityFS\\0' 且 try_bundle 成功、
    且 b.start <= off < b.start+total 即命中。"""
    pos = []
    i = data.find(b"UnityFS\0")
    while i >= 0:
        pos.append(i)
        i = data.find(b"UnityFS\0", i + 1)
    hits = []
    for p in pos:
        if p > off:
            break
        b = K.try_bundle(data, p)
        if b is None:
            continue
        if b["start"] <= off < b["start"] + b["total"]:
            hits.append(b)
            break
    return hits[0] if hits else None


def main(tasks):
    cache = {}
    for fn, off, tag in tasks:
        if fn not in cache:
            cache[fn] = open(os.path.join(BASE, fn), 'rb').read()
        data = cache[fn]
        b = find_bundle(data, off)
        if not b:
            print("%-9s %s @%d 定位失败" % (tag, fn[:12], off))
            continue
        pl = K.bundle_payload(data, b)
        cab = [nd for nd in b["nodes"] if not nd["path"].endswith(".resS")]
        res = [nd for nd in b["nodes"] if nd["path"].endswith(".resS")]
        if not cab or not res:
            print("%-9s 节点缺失" % tag)
            continue
        nd0 = cab[0]
        seg = pl[nd0["offset"]:nd0["offset"] + nd0["size"]]
        try:
            h = K.sf_parse(seg)
        except Exception as e:
            print("%-9s sf 解析失败 %s" % (tag, e))
            continue
        print("=" * 96)
        print("%-9s %s bundle@%d %s 对象=%d  resS=%d" %
              (tag, fn[:12], b["start"], nd0["path"], h["object_count"], res[0]["size"]))
        for o in h["objects"]:
            if o["name"] != "Texture2D":
                continue
            d = K.sf_objdata(h, seg, o)
            t = parse_tex(d)
            if not t or t["off"] is None:
                continue
            raw = pl[res[0]["offset"] + t["off"]:res[0]["offset"] + t["off"] + t["size"]]
            img = to_image(raw, t["w"], t["h"], t["fmt"])
            if img is None:
                print("   %-22s %4dx%-4d fmt=%-7s (不支持)" %
                      (t["name"], t["w"], t["h"], FMT.get(t["fmt"], t["fmt"])))
                continue
            base = "%s_%s_%dx%d" % (tag, t["name"].replace("/", "_"), t["w"], t["h"])
            bg = Image.new("RGBA", img.size, (40, 44, 52, 255))
            bg.alpha_composite(img)
            bg.convert("RGB").resize((img.width * 2, img.height * 2),
                                     Image.LANCZOS).save(os.path.join(OUT, "V_" + base + ".png"))
            img.transpose(Image.FLIP_TOP_BOTTOM).save(os.path.join(OUT, "raw_" + base + ".png"))
            print("   %-22s %4dx%-4d fmt=%-7s off=%-8d -> %s" %
                  (t["name"], t["w"], t["h"], FMT.get(t["fmt"], t["fmt"]),
                   t["off"], "V_" + base + ".png"))


if __name__ == "__main__":
    main([
        ("10d8f3adca3f6d9c0c321cbcf89c72b0.wmv", 31797393, "t12"),
        ("10d8f3adca3f6d9c0c321cbcf89c72b0.wmv", 31806360, "t8a"),
        ("f5ee331203a685423e94d1bec0bbdb4e.wmv", 47628062, "t5"),
        ("f5ee331203a685423e94d1bec0bbdb4e.wmv", 47637192, "t9a"),
        ("5ca670844a1a73364a8ac9d00bfab2c0.wmv", 19830173, "t9b"),
        ("5ca670844a1a73364a8ac9d00bfab2c0.wmv", 10176465, "quantum"),
        ("6d45a4650aab5060c5c31b5431e37bc8.wmv", 750186, "t8b"),
    ])
