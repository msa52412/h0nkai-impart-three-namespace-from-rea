"""列出目标 bundle 内全部 Texture2D 的 resS 偏移/尺寸，确认替换范围。"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmvkit as K

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
FN = "0a95a3510bffb1a31fdef2cae36e8783.wmv"
BIDX = 848


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
    p = q + 4 + 1
    p = (p + 3) & ~3
    w, h = struct.unpack_from("<ii", d, p); p += 8
    cis = struct.unpack_from("<i", d, p)[0]; p += 4
    tf = struct.unpack_from("<i", d, p)[0]
    q2 = d.find(b"archive:/")
    off = None
    if q2 > 0:
        off, size, plen = struct.unpack_from("<III", d, q2 - 12)
    return {"name": name, "w": w, "h": h, "fmt": tf, "cis": cis, "off": off}


data = open(os.path.join(BASE, FN), 'rb').read()
bs = [b for b in [K.try_bundle(data, p) for p in []]]
_, allb = K.walk(data=data)
b = allb[BIDX]
pl = K.bundle_payload(data, b)
print("bundle@%d total=%d payload=%d  nodes=%d" % (b["start"], b["total"], len(pl), len(b["nodes"])))
for nd in b["nodes"]:
    print("   node %-70s off=%-8d size=%d" % (nd["path"], nd["offset"], nd["size"]))
cab = [nd for nd in b["nodes"] if not nd["path"].endswith(".resS")][0]
res = [nd for nd in b["nodes"] if nd["path"].endswith(".resS")][0]
seg = pl[cab["offset"]:cab["offset"] + cab["size"]]
h = K.sf_parse(seg)
print("\n对象数=%d" % h["object_count"])
rows = []
for o in h["objects"]:
    if o["name"] != "Texture2D":
        continue
    d = K.sf_objdata(h, seg, o)
    t = parse_tex(d)
    if t:
        rows.append((t["off"] if t["off"] is not None else -1, t["w"], t["h"], t["fmt"], t["cis"], t["name"], o["path_id"]))
rows.sort()
print("resS 总长=%d" % res["size"])
for off, w, hh, fmt, cis, nm, pid in rows:
    end = off + cis if off >= 0 else -1
    gap = ""
    print("  off=%-8d end=%-8d %4dx%-4d fmt=%-3d cis=%-8d pid=%-20d %s%s" %
          (off, end, w, hh, fmt, cis, pid, nm, gap))
