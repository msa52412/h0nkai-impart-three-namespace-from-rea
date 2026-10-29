"""反查引用：谁引用了 9 个 Sprite 的 pathID，从而定位 Task_N 槽位的图标来源。

MonoBehaviour 里的引用是 PPtr = {i32 fileID, i64 pathID}。
直接在对象数据里搜 pathID 的小端 8 字节即可。
"""
import os
import struct
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmvkit as K

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
FN = "0a95a3510bffb1a31fdef2cae36e8783.wmv"
BIDX = 848


def read_aligned_str(b, p):
    n = struct.unpack_from("<i", b, p)[0]
    if n < 0 or n > 4096 or p + 4 + n > len(b):
        return None, p
    return b[p + 4:p + 4 + n], (p + 4 + n + 3) & ~3


path = os.path.join(BASE, FN)
data = open(path, 'rb').read()
_, bs = K.walk(data=data)
b = bs[BIDX]
pl = K.bundle_payload(data, b)
cab = [nd for nd in b["nodes"] if not nd["path"].endswith(".resS")][0]
seg = pl[cab["offset"]:cab["offset"] + cab["size"]]
h = K.sf_parse(seg)
by_pid = {o["path_id"]: o for o in h["objects"]}

# GameObject 名字表
gname = {}
for o in h["objects"]:
    if o["name"] != "GameObject":
        continue
    d = K.sf_objdata(h, seg, o)
    try:
        n = struct.unpack_from("<i", d, 0)[0]
        p = 4 + n * 12 + 4
        s, q = read_aligned_str(d, p)
        if s:
            gname[o["path_id"]] = s.decode("utf-8", "replace")
    except Exception:
        pass

# MonoBehaviour 头部：m_GameObject(12) + m_Enabled(1) + align? + m_Script(12)
def mb_head(d):
    fid = struct.unpack_from("<i", d, 0)[0]
    pid = struct.unpack_from("<q", d, 4)[0]
    p = 12
    en = d[p]
    p += 1
    # PPtr 需要 4 字节对齐
    p = (p + 3) & ~3
    sfid = struct.unpack_from("<i", d, p)[0]
    spid = struct.unpack_from("<q", d, p + 4)[0]
    return fid, pid, en, sfid, spid


# Sprite 表
sprites = [o for o in h["objects"] if o["name"] in ("Sprite", "Texture2D")]

print("=== 反查引用 ===")
for sp in sprites:
    d0 = K.sf_objdata(h, seg, sp)
    s, _ = read_aligned_str(d0, 0)
    nm = s.decode("utf-8", "replace") if s else "?"
    needle = struct.pack("<q", sp["path_id"])
    refs = []
    for o in h["objects"]:
        if o["path_id"] == sp["path_id"]:
            continue
        d = K.sf_objdata(h, seg, o)
        st = 0
        while True:
            i2 = d.find(needle, st)
            if i2 < 0:
                break
            # 前面 4 字节应是 fileID
            fid = struct.unpack_from("<i", d, i2 - 4)[0] if i2 >= 4 else None
            refs.append((o, i2, fid))
            st = i2 + 1
    print("\n%-14s pid=%-22d %-16s 被引用 %d 次" %
          (sp["name"], sp["path_id"], nm, len(refs)))
    for o, off, fid in refs[:12]:
        extra = ""
        if o["name"] == "MonoBehaviour":
            try:
                d = K.sf_objdata(h, seg, o)
                gfid, gpid, en, sfid, spid = mb_head(d)
                extra = " owner=%r(fid=%d) script=pid%d" % (
                    gname.get(gpid, "?"), gfid, spid)
            except Exception as e:
                extra = " (head 解析失败)"
        print("    <- obj pid=%-22d %-14s off=%-5d refFileID=%s%s" %
              (o["path_id"], o["name"], off, fid, extra))

print("\n=== Task_N GameObject 的组件 ===")
for pid, nm in sorted(gname.items(), key=lambda x: x[1]):
    if not nm.startswith("Task_"):
        continue
    o = by_pid.get(pid)
    d = K.sf_objdata(h, seg, o)
    n = struct.unpack_from("<i", d, 0)[0]
    comps = []
    for i in range(n):
        cfid = struct.unpack_from("<i", d, 4 + i * 12)[0]
        cpid = struct.unpack_from("<q", d, 8 + i * 12)[0]
        co = by_pid.get(cpid)
        comps.append("%s(pid=%d)" % (co["name"] if co else "?", cpid))
    print("  %-8s pid=%-22d 组件: %s" % (nm, pid, ", ".join(comps)))
