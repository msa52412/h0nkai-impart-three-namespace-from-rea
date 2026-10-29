"""解析 bundle#848 的 UI 结构：
  - 所有 Sprite / Texture2D 的名字（槽位图标候选）
  - 所有 GameObject 的名字（Task_1..9）
  - MonoBehaviour 头部（m_GameObject / m_Script）与内部 PPtr 引用
输出便于定位「Task_3 槽位用的是哪个 Sprite」。
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmvkit as K

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
FN = "0a95a3510bffb1a31fdef2cae36e8783.wmv"
BIDX = 848


def read_aligned_str(b, p):
    n = struct.unpack_from("<i", b, p)[0]
    if n < 0 or n > 4096 or p + 4 + n > len(b):
        return None, p
    s = b[p + 4:p + 4 + n]
    q = (p + 4 + n + 3) & ~3
    return s, q


def pptr(b, p):
    fid = struct.unpack_from("<i", b, p)[0]
    pid = struct.unpack_from("<q", b, p + 4)[0]
    return fid, pid, p + 12


path = os.path.join(BASE, FN)
data = open(path, 'rb').read()
_, bs = K.walk(data=data)
b = bs[BIDX]
print("bundle#%d @%d total=%d blocks=%d nodes=%d" %
      (BIDX, b["start"], b["total"], b["block_count"], b["node_count"]))
for nd in b["nodes"]:
    print("  node %-70s off=%-8d size=%d" % (nd["path"][:70], nd["offset"], nd["size"]))

pl = K.bundle_payload(data, b)
print("payload 总长:", len(pl))

# 找 CAB 节点
cab = None
for nd in b["nodes"]:
    if not nd["path"].endswith(".resS"):
        cab = nd
        break
seg = pl[cab["offset"]:cab["offset"] + cab["size"]]
h = K.sf_parse(seg)
print("SerializedFile: %d 对象, dataOffset=%d, types=%d" %
      (h["object_count"], h["data_offset"], h["type_count"]))

# 类型统计
from collections import Counter
cnt = Counter(o["name"] for o in h["objects"])
print("类型:", cnt.most_common())

print("\n===== Sprite / Texture2D =====")
for o in h["objects"]:
    if o["name"] in ("Sprite", "Texture2D"):
        d = K.sf_objdata(h, seg, o)
        s, q = read_aligned_str(d, 0)
        extra = ""
        if o["name"] == "Texture2D" and s is not None:
            # m_Name, m_ForcedFallbackFormat(i32), m_DownscaleFallback(u8), align?, m_Width, m_Height
            try:
                p = q
                fmt = struct.unpack_from("<i", d, p)[0]; p += 4
                ds = d[p]; p += 1
                p = (p + 3) & ~3
                w, hh = struct.unpack_from("<ii", d, p)
                extra = " %dx%d" % (w, hh)
            except Exception:
                pass
        print("  pid=%-22d %-10s size=%-6d name=%r%s" %
              (o["path_id"], o["name"], o["byte_size"],
               s.decode("utf-8", "replace") if s else None, extra))

print("\n===== GameObject 名字 =====")
gos = []
for o in h["objects"]:
    if o["name"] != "GameObject":
        continue
    d = K.sf_objdata(h, seg, o)
    try:
        n = struct.unpack_from("<i", d, 0)[0]
        if not (0 <= n <= 64):
            continue
        p = 4 + n * 12
        layer = struct.unpack_from("<i", d, p)[0]
        p += 4
        s, q = read_aligned_str(d, p)
        if s is None:
            continue
        name = s.decode("utf-8", "replace")
        gos.append((o["path_id"], name, o["byte_size"]))
    except Exception:
        continue
print("  解析出 %d / %d 个 GameObject 名字" %
      (len(gos), sum(1 for o in h["objects"] if o["name"] == "GameObject")))
for pid, name, sz in gos:
    if any(k in name for k in ("Task", "Cover", "Challenge", "Icon", "Entry")):
        print("    pid=%-22d %-40r size=%d" % (pid, name, sz))

print("\n===== 名字含 Task 的全部对象（任意类型）=====")
for o in h["objects"]:
    d = K.sf_objdata(h, seg, o)
    if b"Task_" in d:
        idx = d.find(b"Task_")
        print("  obj pid=%-22d %-14s size=%-6d off=%d ctx=%r" %
              (o["path_id"], o["name"], o["byte_size"], idx,
               d[max(0, idx - 24):idx + 32]))

print("\n===== MonoScript（用于反查类名）=====")
for o in h["objects"]:
    if o["name"] != "MonoScript":
        continue
    d = K.sf_objdata(h, seg, o)
    s0, p1 = read_aligned_str(d, 0)   # m_Name
    s1, p2 = read_aligned_str(d, p1)  # m_ClassName
    s2, p3 = read_aligned_str(d, p2)  # m_Namespace
    s3, p4 = read_aligned_str(d, p3)  # m_AssemblyName
    print("  pid=%-22d class=%-34r ns=%-22r asm=%r" %
          (o["path_id"],
           s1.decode("utf-8", "replace") if s1 else None,
           s2.decode("utf-8", "replace") if s2 else None,
           s3.decode("utf-8", "replace") if s3 else None))
