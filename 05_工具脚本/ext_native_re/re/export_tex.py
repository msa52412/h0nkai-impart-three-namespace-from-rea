"""从 .wmv 里提取 Texture2D 像素并导出 PNG。

m_StreamData 定位用启发式：在 Texture2D 对象数据里找 b"archive:/"，
其前 12 字节为 u32 offset、前 8 字节为 u32 size。
支持 RGBA32(4) / RGB24(3) / ARGB32(5) / DXT1(10) / DXT5(12) 等常见格式的探测。
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmvkit as K

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
    """返回 dict 或 None"""
    s, q = rs(d, 0)
    if s is None:
        return None
    name = s.decode("utf-8", "replace")
    p = q
    try:
        forced = struct.unpack_from("<i", d, p)[0]; p += 4
        p += 1                                   # m_DownscaleFallback
        p = (p + 3) & ~3
        w, h = struct.unpack_from("<ii", d, p); p += 8
        cis = struct.unpack_from("<i", d, p)[0]; p += 4
        tf = struct.unpack_from("<i", d, p)[0]; p += 4
        mip = struct.unpack_from("<i", d, p)[0]; p += 4
    except Exception:
        return None
    q2 = d.find(b"archive:/")
    if q2 < 0:
        return {"name": name, "w": w, "h": h, "fmt": tf, "size": cis,
                "off": None, "path": None}
    off, size, plen = struct.unpack_from("<III", d, q2 - 12)
    path = d[q2:q2 + plen].decode("ascii", "replace")
    return {"name": name, "w": w, "h": h, "fmt": tf, "size": cis,
            "mip": mip, "off": off, "path": path}


def to_image(raw, w, h, tf):
    if tf == 4:      # RGBA32
        return Image.frombytes("RGBA", (w, h), raw[:w * h * 4])
    if tf == 3:      # RGB24
        return Image.frombytes("RGB", (w, h), raw[:w * h * 3])
    if tf == 5:      # ARGB32
        img = Image.frombytes("RGBA", (w, h), raw[:w * h * 4])
        return img
    if tf == 14:     # BGRA32
        return Image.frombytes("RGBA", (w, h), raw[:w * h * 4]).convert("RGBA")
    return None


def dump_file(fn, bidx, tag):
    path = os.path.join(BASE, fn)
    data = open(path, 'rb').read()
    _, bs = K.walk(data=data)
    b = bs[bidx]
    pl = K.bundle_payload(data, b)
    nodes = {nd["path"]: nd for nd in b["nodes"]}
    cab = [nd for nd in b["nodes"] if not nd["path"].endswith(".resS")][0]
    seg = pl[cab["offset"]:cab["offset"] + cab["size"]]
    h = K.sf_parse(seg)
    print("=" * 92)
    print("%s bundle#%d  %s" % (fn[:16], bidx, cab["path"]))
    for o in h["objects"]:
        if o["name"] != "Texture2D":
            continue
        d = K.sf_objdata(h, seg, o)
        t = parse_tex(d)
        if not t:
            print("  解析失败 pid=%d" % o["path_id"])
            continue
        info = "%-24s %4dx%-4d fmt=%-7s size=%-7d" % (
            t["name"], t["w"], t["h"], FMT.get(t["fmt"], t["fmt"]), t["size"])
        if t["off"] is None:
            print("  " + info + " (无 streamdata)")
            continue
        # 找对应 resS node
        base = t["path"].split("/")[-1]
        nd = None
        for k, v in nodes.items():
            if k.endswith(base) or base.endswith(k.split("/")[-1]):
                nd = v
                break
        if nd is None:
            print("  " + info + " !! 找不到 resS")
            continue
        raw = pl[nd["offset"] + t["off"]:nd["offset"] + t["off"] + t["size"]]
        img = to_image(raw, t["w"], t["h"], t["fmt"])
        if img is None:
            print("  " + info + " !! 不支持格式 %d" % t["fmt"])
            continue
        outn = "%s_%s_%dx%d.png" % (tag, t["name"].replace("/", "_"), t["w"], t["h"])
        img.save(os.path.join(OUT, outn))
        print("  " + info + " off=%-8d -> %s" % (t["off"], outn))


dump_file("0a95a3510bffb1a31fdef2cae36e8783.wmv", 848, "challenge")
dump_file("a760d70eb463ac3e290a733cfd35d18f.wmv", 87, "wm87")
dump_file("a760d70eb463ac3e290a733cfd35d18f.wmv", 120, "wm120")
