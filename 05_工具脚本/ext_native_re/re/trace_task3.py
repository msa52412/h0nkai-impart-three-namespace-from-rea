"""追踪 Task_3 槽位：父子链、挂的 MonoBehaviour 内容、图标来源。"""
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


path = os.path.join(BASE, FN)
data = open(path, 'rb').read()
_, bs = K.walk(data=data)
b = bs[BIDX]
pl = K.bundle_payload(data, b)
cab = [nd for nd in b["nodes"] if not nd["path"].endswith(".resS")][0]
seg = pl[cab["offset"]:cab["offset"] + cab["size"]]
h = K.sf_parse(seg)
by = {o["path_id"]: o for o in h["objects"]}
od = {o["path_id"]: K.sf_objdata(h, seg, o) for o in h["objects"]}

# GameObject 名
gname = {}
for o in h["objects"]:
    if o["name"] != "GameObject":
        continue
    d = od[o["path_id"]]
    try:
        n = struct.unpack_from("<i", d, 0)[0]
        s, _ = rs(d, 4 + n * 12 + 4)
        if s:
            gname[o["path_id"]] = s.decode("utf-8", "replace")
    except Exception:
        pass

# Transform 树：path_id -> (gameObject pid, father pid, children[])
tf = {}
for o in h["objects"]:
    if o["name"] not in ("Transform", "RectTransform"):
        continue
    d = od[o["path_id"]]
    try:
        gpid = struct.unpack_from("<q", d, 4)[0]
        p = 12 + 16 + 12 + 12          # rotation + position + scale
        cn = struct.unpack_from("<i", d, p)[0]
        p += 4
        kids = [struct.unpack_from("<q", d, p + i * 12 + 4)[0] for i in range(cn)]
        p += cn * 12
        fpid = struct.unpack_from("<q", d, p + 4)[0]
        tf[o["path_id"]] = (gpid, fpid, kids)
    except Exception:
        pass

print("Transform 解析: %d / %d" % (len(tf), sum(1 for o in h["objects"]
                                              if o["name"] in ("Transform", "RectTransform"))))

go2tf = {v[0]: k for k, v in tf.items()}


def path_of(gpid, depth=0):
    """游戏对象 -> 从根到自身的路径"""
    if depth > 40:
        return ["..."]
    t = go2tf.get(gpid)
    if t is None:
        return [gname.get(gpid, "?")]
    father = tf[t][1]
    up = path_of(tf[father][0], depth + 1) if father in tf else []
    return up + [gname.get(gpid, "?")]


print("\n=== Task_N 组件 + 层级路径 ===")
tgt = None
for gpid, nm in sorted(gname.items(), key=lambda x: x[1]):
    if not nm.startswith("Task_"):
        continue
    t = go2tf.get(gpid)
    d = od[gpid]
    n = struct.unpack_from("<i", d, 0)[0]
    comps = []
    for i in range(n):
        cpid = struct.unpack_from("<q", d, 8 + i * 12)[0]
        co = by.get(cpid)
        comps.append("%s" % (co["name"] if co else "?"))
    pth = "/".join(path_of(gpid))
    print("  %-8s %s" % (nm, pth))
    print("     组件: %s" % ", ".join(comps))
    # 子对象
    kids = tf[t][2] if t in tf else []
    for k in kids:
        kgo = tf[k][0]
        print("       子: %-24s [%s]" % (gname.get(kgo, "?"),
              ",".join(by[x[1] and 0 or 0]["name"] if False else "" for x in [])))
    if nm == "Task_3":
        tgt = gpid

print("\n=== Task_3 子树完整展开 ===")


def dump_sub(gpid, ind=0):
    t = go2tf.get(gpid)
    print("  " * ind + "- %s" % gname.get(gpid, "?"))
    if t is None:
        return
    for k in tf[t][2]:
        dump_sub(tf[k][0], ind + 1)


if tgt:
    dump_sub(tgt)

print("\n=== Task_3 的 MonoBehaviour 数据 ===")
d0 = od[tgt]
n = struct.unpack_from("<i", d0, 0)[0]
for i in range(n):
    cpid = struct.unpack_from("<q", d0, 8 + i * 12)[0]
    co = by.get(cpid)
    if not co or co["name"] != "MonoBehaviour":
        continue
    d = od[cpid]
    print("\n  MonoBehaviour pid=%d size=%d" % (cpid, co["byte_size"]))
    print("  hex:", d.hex())
    # 可读串
    strs = []
    j = 0
    while j < len(d):
        if 32 <= d[j] < 127:
            k = j
            while k < len(d) and 32 <= d[k] < 127:
                k += 1
            if k - j >= 3:
                strs.append((j, d[j:k].decode()))
            j = k
        else:
            j += 1
    print("  strings:", strs)
    # 内部 PPtr 候选（i32 + i64 pattern where i64 looks like pathID）
    for off in range(0, len(d) - 12, 4):
        fid = struct.unpack_from("<i", d, off)[0]
        pid = struct.unpack_from("<q", d, off + 4)[0]
        if fid in (0, 1) and pid in by:
            print("    PPtr@%d -> %s pid=%d" % (off, by[pid]["name"], pid))
        elif fid not in (0, 1) and pid in by:
            print("    PPtr@%d fileID=%d -> %s pid=%d" % (off, fid, by[pid]["name"], pid))
