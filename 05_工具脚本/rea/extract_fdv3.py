# -*- coding: utf-8 -*-
"""fieldDefaultValues v3：按枚举底层类型（value__ 字段的类型）宽度读值
   宽度来源：bh3_fields.tsv 的 fieldType 列"""
import struct
from collections import defaultdict

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
POOL = 0x1D79938
SENT = 0xFFFFFFFF

# 1) 字段表: fi -> (typeIdx, typeName, fieldName, fieldType)
fields = {}
for ln in open(r"D:\Carol-start\_rea\bh3_fields.tsv", encoding="utf-8", errors="replace"):
    p = ln.rstrip("\n").split("\t")
    if len(p) >= 5 and p[0] != "typeIdx":
        try:
            fields[int(p[2])] = (int(p[0]), p[1], p[3], p[4])
        except ValueError:
            pass

# 2) 枚举底层类型: typeIdx -> width（value__ 的 fieldType）
PRIM_W = {"byte": 1, "sbyte": 1, "ushort": 2, "short": 2,
          "uint": 4, "int": 4, "long": 8, "ulong": 8,
          "float": 4, "double": 8, "bool": 1, "char": 2, "string": 0}
enum_w = {}
for fi, (ti, tn, fn, ft) in fields.items():
    if fn == "value__":
        enum_w[ti] = PRIM_W.get(ft, 4)

# 3) 重读默认值表
rows = []
off = 0x564210
prev_fi = -1
prev_c1 = -1
while off + 12 <= len(BUF):
    fi, c1, c2 = struct.unpack_from("<3I", BUF, off)
    if fi >= 419568 or fi <= prev_fi:
        break
    if c1 != SENT and (c1 < prev_c1 or POOL + c1 + 8 > len(BUF)):
        break
    rows.append((fi, c1, c2))
    prev_fi = fi
    if c1 != SENT:
        prev_c1 = c1
    off += 12

# 4) 按 (字段类型, 枚举宽度) 渲染值
def read_val(fi, c1):
    ti, tn, fn, ft = fields.get(fi, (None, "", "", "int"))
    if ft == "string":
        return None, "str"
    w = enum_w.get(ti, PRIM_W.get(ft, 4))
    if w == 0:
        return None, "str"
    o = POOL + c1
    if w == 1:
        return BUF[o], "u8"
    if w == 2:
        return struct.unpack_from("<H", BUF, o)[0], "u16"
    if w == 4:
        v = struct.unpack_from("<I", BUF, o)[0]
        return (v, "f32") if ft == "float" else (v, "u32")
    if w == 8:
        return struct.unpack_from("<Q", BUF, o)[0], "u64"

with open(r"D:\Carol-start\_rea\bh3_field_defaults.tsv", "w", encoding="utf-8", newline="\n") as f:
    f.write("fieldIdx\tdataOffset\tcol2\tkind\tvalue\n")
    n_v = 0
    for fi, c1, c2 in rows:
        if c1 == SENT:
            f.write("%d\t-1\t-1\tsentinel\t-1\n" % fi)
            continue
        ti, tn, fn, ft = fields.get(fi, (None, "", "", "int"))
        if ft == "string":
            L = struct.unpack_from("<i", BUF, POOL + c1)[0]
            try:
                s = BUF[POOL + c1 + 4:POOL + c1 + 4 + L].decode("utf-8")
            except UnicodeDecodeError:
                s = ""
            f.write("%d\t%d\t%d\tstring\t%s\n" % (fi, c1, c2, s.replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")))
        else:
            v, kind = read_val(fi, c1)
            f.write("%d\t%d\t%d\t%s\t%d\n" % (fi, c1, c2, kind, v))
            n_v += 1
print("表行 %d, 数值 %d + string 行" % (len(rows), n_v))

# 5) 验证 RuneType / DayOfWeek / AttributeTargets
check = {}
for fi, c1, c2 in rows:
    ti, tn, fn, ft = fields.get(fi, (None, "", "", ""))
    if tn.endswith(".RuneType") or tn == "System.DayOfWeek" or tn == "System.AttributeTargets":
        v, kind = read_val(fi, c1) if c1 != SENT else (None, "")
        if v is not None:
            check[(tn.split(".")[-1], fn)] = v
for k in sorted(check):
    print("  %s.%s = %d" % (k[0], k[1], check[k]))
