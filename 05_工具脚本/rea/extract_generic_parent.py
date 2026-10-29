#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v4：继承树终局 —— 泛型基类（Il2CTYPE type 0x15）解析

链路（依据 FUN_180432a60 反编译）:
  parent 字段值 = Il2CTYPE 索引
    -> PTR_TABLE[idx] = 条目 VA (12 字节 {u64 data; u16; u8 type@10; u8 bits@11})
    -> type==0x15: data = Il2CppGenericClass*
         +0x00 u32  typeDefinitionIndex  <-- 泛型定义（如 List`1）
         +0x08 ptr  class_inst: Il2CppGenericInst {u32 argc; u32 pad; Il2CppType** argv}
         +0x18 ptr  cached_class
    -> type==0x11/0x12: data = typeDefinitionIndex 直接
"""
import struct
from collections import Counter, defaultdict

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
OUT_TXT = r"D:\Carol-start\_rea\bh3_types_v4.txt"
OUT_TREE = r"D:\Carol-start\_rea\bh3_inheritance_v4.txt"
OUT_GEN = r"D:\Carol-start\_rea\bh3_generic_parents.txt"

BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x5C
NT = 57487
TBL_VA = 0x186D41F80

d = open(DLL, "rb").read()
e = struct.unpack_from("<I", d, 0x3C)[0]
coff = e + 4
nsec = struct.unpack_from("<H", d, coff + 2)[0]
optsz = struct.unpack_from("<H", d, coff + 16)[0]
opt = coff + 20
IB = struct.unpack_from("<Q", d, opt + 24)[0]
SECS = []
sh = opt + optsz
for i in range(nsec):
    o = sh + i * 40
    name = d[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((name, va, vs, rs, rp))


def va2off(va):
    rva = va - IB
    for name, vaddr, vsize, rsize, rptr in SECS:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return None if rsize == 0 else rptr + (rva - vaddr)
    return None


tbl_off = va2off(TBL_VA)
_u32 = struct.Struct("<I")
_u64 = struct.Struct("<Q")

# 指针表实际长度（.rdata 内连续指针）
N_PTR = 0
_lo, _hi = 0x186C56000, 0x188D09E64
while N_PTR < 600000:
    _p = _u64.unpack_from(d, tbl_off + N_PTR * 8)[0]
    if not (_lo <= _p < _hi):
        break
    N_PTR += 1


def entry_va(idx):
    # parent / byval 等字段值是指针表索引，表长 354,184，远大于 typedef 数 57,487
    if idx < 0 or idx >= N_PTR:
        return None
    return _u64.unpack_from(d, tbl_off + idx * 8)[0]


def entry(idx):
    """返回 (data_u64, type, bits)"""
    p = entry_va(idx)
    if p is None:
        return None
    o = va2off(p)
    if o is None:
        return None
    return _u64.unpack_from(d, o)[0], d[o + 10], d[o + 11]


# ---------- metadata 类型表 ----------
BUF = open(META, "rb").read()
FSIZE = len(BUF)
TYPE_OFF = (_u32.unpack_from(d, va2off(0x188198E08))[0] ^ 0x2B849DB3) & M32
POOL_OFF = _u32.unpack_from(d, va2off(0x188198E50))[0] ^ 0x7483FF7A
K_MUL = (-0x394A88E12FFFF3A0) & M64
K_ADD = 0x53DB1FC7E9ECC644
K_STEP = 0x64C7CE0352814CF6
T0 = BASE + TYPE_OFF
P_ABS = BASE + POOL_OFF

SALT = []
for i in range(NT):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    SALT.append(((x * 0x1125F1B6) & M64) & M32)
S16 = [(SALT[i] & 0xFFFF) - 0x10000 if SALT[i] & 0x8000 else (SALT[i] & 0xFFFF) for i in range(NT)]

_sc = {}


def dec(pid):
    if pid in _sc:
        return _sc[pid]
    L = (pid >> 24) & 0xFF
    if L == 0 or L > 0x80:
        _sc[pid] = None
        return None
    ix = pid & 0xFFFFFF
    src = P_ABS + ix
    nb = (L + 7) >> 3
    if src + nb * 8 > FSIZE:
        _sc[pid] = None
        return None
    key = (ix * K_MUL + K_ADD) & M64
    out = bytearray()
    for b in range(nb):
        out += (_u64.unpack_from(BUF, src + b * 8)[0] ^ key).to_bytes(8, "little")
        key = (key + K_STEP) & M64
    try:
        t = out[:L].decode("utf-8")
    except UnicodeDecodeError:
        _sc[pid] = None
        return None
    for ch in t:
        if ord(ch) < 0x20 or ord(ch) == 0x7F:
            _sc[pid] = None
            return None
    _sc[pid] = t
    return t


recs = []
for i in range(NT):
    off = T0 + i * STEP
    r = struct.unpack_from("<23I", BUF, off)
    s = SALT[i]
    name = dec((((r[13] ^ 0x3399EFB) - s) & M32))
    ns = dec(((((r[12] - s) & M32) - 0x4B6ACCC7) & M32)) or ""
    par = ((r[0] - 0x15F045CB) - s) & M32
    byv = ((r[10] - 0x67AD6F69) - s) & M32
    ms = ((r[5] - 0x2822B502) - s) & M32
    r16 = struct.unpack_from("<H", BUF, off + 0x48)[0]
    s16r = r16 - 0x10000 if r16 & 0x8000 else r16
    mc = (s16r + 0x1950 - S16[i]) & 0xFFFF
    r16n = struct.unpack_from("<H", BUF, off + 0x46)[0]
    nc = ((r16n ^ 0x7883) - S16[i]) & 0xFFFF
    tok = ((r[22] ^ 0x78647F39) - s) & M32
    recs.append({"i": i, "ns": ns, "name": name, "par": par, "byval": byv,
                 "ms": -1 if ms == M32 else ms, "mc": mc, "nc": nc, "tok": tok})


def full(i):
    if i is None or i < 0 or i >= NT:
        return "?"
    return (recs[i]["ns"] + "." if recs[i]["ns"] else "") + (recs[i]["name"] or "?")


PRIM = {0x01: "void", 0x02: "bool", 0x03: "char", 0x04: "sbyte", 0x05: "byte",
        0x06: "short", 0x07: "ushort", 0x08: "int", 0x09: "uint", 0x0A: "long",
        0x0B: "ulong", 0x0C: "float", 0x0D: "double", 0x0E: "string",
        0x18: "System.IntPtr", 0x19: "System.UIntPtr", 0x16: "System.TypedReference"}

_stats = Counter()


def render_ptr(va, depth):
    """data 字段当指针用：指向另一条 Il2CppType"""
    o = va2off(va) if va else None
    if o is None:
        return "<badptr>"
    return render(_u64.unpack_from(d, o)[0], d[o + 10], depth)


def render(data, ty, depth):
    if depth > 6:
        return "..."
    if ty in (0x11, 0x12):          # VALUETYPE / CLASS
        return full(data) if data < NT else "<ty%02X:%X>" % (ty, data)
    if ty == 0x1C:
        return "System.Object"
    if ty == 0x15:                  # GENERICINST
        _stats["gen"] += 1
        go = va2off(data)
        if go is None:
            return "<genptr>"
        defIdx = _u32.unpack_from(d, go)[0]
        base = full(defIdx)
        ci = _u64.unpack_from(d, go + 8)[0]
        args = gen_args(ci, depth + 1)
        return base + ("<%s>" % ",".join(args) if args else "")
    if ty == 0x1D:                  # SZARRAY
        return render_ptr(data, depth + 1) + "[]"
    if ty == 0x14:                  # ARRAY
        ao = va2off(data)
        if ao is None:
            return "<arrptr>"
        et = _u64.unpack_from(d, ao)[0]
        rank = _u32.unpack_from(d, ao + 8)[0]
        return render_ptr(et, depth + 1) + "[" + "," * max(rank - 1, 0) + "]"
    if ty == 0x0F:
        return render_ptr(data, depth + 1) + "*"
    if ty == 0x10:
        return render_ptr(data, depth + 1) + "&"
    if ty == 0x13:
        return "!%d" % data
    if ty == 0x1E:
        return "!!%d" % data
    return PRIM.get(ty, "<ty%02X>" % ty)


def gen_args(ci, depth):
    if not ci or depth > 6:
        return []
    co = va2off(ci)
    if co is None:
        return []
    argc = _u32.unpack_from(d, co)[0]
    argv = _u64.unpack_from(d, co + 8)[0]
    ao = va2off(argv) if argv else None
    if ao is None or argc > 16:
        return []
    out = []
    for k in range(argc):
        tp = _u64.unpack_from(d, ao + k * 8)[0]
        out.append(render_ptr(tp, depth + 1))
    return out


# ---------- parent 解析 ----------
import re

_VARRE = re.compile(r"(?<!!)!(?!\!)(\d+)")


def param_count(i):
    n = recs[i]["name"] or ""
    if "`" in n:
        try:
            return int(n.rsplit("`", 1)[1])
        except ValueError:
            return 0
    return 0


def normalize_var(ci, s):
    """把全局 genericParamIndex 的 !n 还原为声明序 T0/T1

    依据：GenericParam 表按声明序分配全局索引，故升序即 T0,T1,...
    已验证 38 条「基类只引用部分形参」的情形（如 EnumerableTypeInfo`2 ->
    TraceLoggingTypeInfo`1<T0>、WhereSelectEnumerableIterator`2 -> Iterator`1<T0>）
    均与 .NET / FullInspector 源码一致。
    """
    if "!" not in s:
        return s
    idxs = sorted({int(m) for m in _VARRE.findall(s)})
    if not idxs:
        return s
    mp = {k: "T%d" % n for n, k in enumerate(idxs)}
    return _VARRE.sub(lambda m: mp.get(int(m.group(1)), m.group(0)), s)


TYPECLASS = {0x11, 0x12}
kind = Counter()
gen_list = []
for rec in recs:
    p = rec["par"]
    if p == M32:
        rec["pfull"] = ""
        rec["pidx"] = None
        kind["nil"] += 1
        continue
    en = entry(p)
    if en is None:
        rec["pfull"] = "<bad idx %d>" % p
        kind["badidx"] += 1
        continue
    data, ty, bits = en
    if ty in TYPECLASS and data < NT:
        rec["pfull"] = full(data)
        rec["pidx"] = data
        kind["class"] += 1
    elif ty == 0x15:
        rec["pfull"] = normalize_var(rec["i"], render(data, ty, 0))
        rec["pidx"] = None
        kind["generic"] += 1
        gen_list.append((rec["i"], rec["pfull"]))
    else:
        rec["pfull"] = normalize_var(rec["i"], render(data, ty, 0))
        rec["pidx"] = None
        kind["other_%02X" % ty] += 1

print("[parent 解析] 直接类: %d / 泛型: %d / nil: %d / 坏索引: %d / 其他: %s"
      % (kind["class"], kind["generic"], kind["nil"], kind["badidx"],
         {k: v for k, v in kind.items() if k.startswith("other_")}))

# ---------- 泛型基类明细 ----------
gc = Counter(x[1] for x in gen_list)
print("\n[泛型基类] 唯一泛型基类形态 = %d" % len(gc))
print("Top 20:")
for k, v in gc.most_common(20):
    print("  %-58s %4d" % (k, v))

with open(OUT_GEN, "w", encoding="utf-8") as f:
    f.write("# 泛型基类（Il2CTYPE type 0x15）解析结果\n")
    f.write("# 共 %d 个子类 / %d 种泛型基类形态\n\n" % (len(gen_list), len(gc)))
    f.write("## 按基类聚合\n")
    byg = defaultdict(list)
    for ci, pf in gen_list:
        byg[pf].append(ci)
    for pf in sorted(byg, key=lambda k: -len(byg[k])):
        f.write("\n### %s  (%d 个子类)\n" % (pf, len(byg[pf])))
        for ci in byg[pf]:
            f.write("    [%6d] %s\n" % (ci, full(ci)))
    f.write("\n\n## 按子类索引\n")
    for ci, pf in gen_list:
        f.write("%6d\t%s\t%s\n" % (ci, full(ci), pf))
print("\n[+] %s" % OUT_GEN)

# ---------- 输出 v4 ----------
with open(OUT_TXT, "w", encoding="utf-8") as f:
    f.write("index\tnamespace\ttype\ttoken\tmethodStart\tmethodCount\tnestedCount\tparentIdx\tparent\n")
    for r in recs:
        f.write("%d\t%s\t%s\t%08X\t%d\t%d\t%d\t%d\t%s\n"
                % (r["i"], r["ns"], r["name"] or "", r["tok"], r["ms"], r["mc"], r["nc"],
                   -1 if r["par"] == M32 else r["par"], r.get("pfull", "")))
print("[+] %s (v4)" % OUT_TXT)

# ---------- 继承树（按父类名聚合，含泛型） ----------
children = defaultdict(list)
for r in recs:
    if r.get("pfull"):
        children[r["pfull"]].append(r["i"])

with open(OUT_TREE, "w", encoding="utf-8") as f:
    f.write("# 继承树（v4，含泛型基类解析）  共 %d 条边\n" % sum(len(v) for v in children.values()))
    for pn in sorted(children, key=lambda k: -len(children[k])):
        f.write("\n### %s  (%d 个子类)\n" % (pn, len(children[pn])))
        for ci in children[pn][:500]:
            f.write("    %s\n" % full(ci))
print("[+] %s" % OUT_TREE)

print("\n[父类频次 Top 15]")
for k, v in Counter(r["pfull"] for r in recs if r.get("pfull")).most_common(15):
    print("  %-58s %6d" % (k, v))

# ---------- 锚点验证 ----------
print("\n[锚点验证]")
checks = [("System.String", "System.Object"), ("System.Exception", "System.Object"),
          ("System.Int32", "System.ValueType"), ("System.Enum", "System.ValueType"),
          ("UnityEngine.GameObject", "UnityEngine.Object"), ("System.Object", "")]
for t, want in checks:
    ns, _, tn = t.rpartition(".")
    r = next((x for x in recs if x["name"] == tn and x["ns"] == ns), None)
    got = r["pfull"] if r else "<未找到>"
    print("  %-26s -> %-34s %s" % (t, got, "OK" if got == want else "期望 %s" % want))

# ---------- 深度（含泛型父类） ----------
byname = {}
for r in recs:
    byname[full(r["i"])] = r


def depth_of(i, seen=None):
    if seen is None:
        seen = set()
    if i in seen or i >= NT:
        return 0
    seen.add(i)
    p = recs[i].get("pidx")
    if p is None:
        return 1
    return 1 + depth_of(p, seen)


print("\n[最深继承链 Top 3]")
for i in sorted(range(NT), key=lambda i: -depth_of(i))[:3]:
    chain = []
    j = i
    for _ in range(16):
        chain.append(full(j))
        pj = recs[j].get("pidx")
        if pj is None:
            break
        j = pj
    print("  (%d) %s" % (depth_of(i), " -> ".join(chain)))
