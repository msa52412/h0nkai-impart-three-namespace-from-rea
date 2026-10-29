#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字段表提取（v1）

表位置：abs = 0x118 + (DAT_188198E84 - 0x2F59FE76) = 0x1F5D9D8
记录 12 字节 {u32 A; u32 typeIdx; u32 nameId}，全部以 prf(globalFieldIdx) 混淆：
  prf(i) = ((i * 0x7740EEFF55F40540 + 0x49ED7F5AFCC4AF8) >> 0x11) & 0xFFFFFFFF
  nameId  = (rec[2] ^ 0x5DAAB140) - prf
  typeIdx = (rec[1] - prf) - 0xF2A3D7F      -> Il2CTYPE 索引
  raw A   = (rec[0] - prf)

每类型 fieldStart = (record[0x1C] - salt) + 0xAA6F650E  （-1 表示无字段）
每类型字段数 = 下一个 start 的差分（字段表全局连续）
"""
import struct
from collections import Counter

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
OUT = r"D:\Carol-start\_rea\bh3_fields.txt"

BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x5C
NT = 57487
TBL_CTYPE = 0x186D41F80

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
    nm = d[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((nm, va, vs, rs, rp))


def va2off(va):
    rva = va - IB
    for nm, vaddr, vsize, rsize, rptr in SECS:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return None if rsize == 0 else rptr + (rva - vaddr)
    return None


def u32va(va):
    o = va2off(va)
    return None if o is None else struct.unpack_from("<I", d, o)[0]


BUF = open(META, "rb").read()
FSIZE = len(BUF)
TYPE_OFF = (u32va(0x188198E08) ^ 0x2B849DB3) & M32
POOL_OFF = u32va(0x188198E50) ^ 0x7483FF7A
FLD_OFF = (u32va(0x188198E84) - 0x2F59FE76) & M32
K_MUL = (-0x394A88E12FFFF3A0) & M64
K_ADD = 0x53DB1FC7E9ECC644
K_STEP = 0x64C7CE0352814CF6
T0 = BASE + TYPE_OFF
P_ABS = BASE + POOL_OFF
F0 = BASE + FLD_OFF
_u64 = struct.Struct("<Q")

SALT = []
for i in range(NT):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    SALT.append(((x * 0x1125F1B6) & M64) & M32)

_sc = {}


def dec(pid):
    if pid in _sc:
        return _sc[pid]
    L = (pid >> 24) & 0xFF
    if L == 0:
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


# ---------- 类型名 ----------
recs = []
for i in range(NT):
    off = T0 + i * STEP
    r = struct.unpack_from("<23I", BUF, off)
    s = SALT[i]
    nm = dec((((r[13] ^ 0x3399EFB) - s) & M32))
    ns = dec(((((r[12] - s) & M32) - 0x4B6ACCC7) & M32)) or ""
    recs.append({"i": i, "ns": ns, "name": nm, "r7": r[7], "s": s})


def full(i):
    return (recs[i]["ns"] + "." if recs[i]["ns"] else "") + (recs[i]["name"] or "?")


# ---------- 字段表 ----------
K1 = 0x7740EEFF55F40540
K2 = 0x49ED7F5AFCC4AF8


def prf(i):
    return (((i * K1 + K2) & M64) >> 0x11) & M32


tbl_off = va2off(TBL_CTYPE)
PRIM = {0x01: "void", 0x02: "bool", 0x03: "char", 0x04: "sbyte", 0x05: "byte",
        0x06: "short", 0x07: "ushort", 0x08: "int", 0x09: "uint", 0x0A: "long",
        0x0B: "ulong", 0x0C: "float", 0x0D: "double", 0x0E: "string",
        0x16: "System.TypedReference", 0x18: "System.IntPtr", 0x19: "System.UIntPtr"}


def ctype(idx, depth=0):
    if idx == M32 or idx >= 354184 or depth > 5:
        return "<nil>" if idx == M32 else "<oob>"
    p = struct.unpack_from("<Q", d, tbl_off + idx * 8)[0]
    po = va2off(p)
    if po is None:
        return "<badptr>"
    data = struct.unpack_from("<Q", d, po)[0]
    ty = d[po + 10]
    if ty in (0x11, 0x12):
        return full(data) if data < NT else "<ty%02X>" % ty
    if ty == 0x1C:
        return "System.Object"
    if ty == 0x15:
        go = va2off(data)
        if go is None:
            return "<genptr>"
        base = full(struct.unpack_from("<I", d, go)[0])
        ci = struct.unpack_from("<Q", d, go + 8)[0]
        co = va2off(ci)
        if co is None:
            return base
        argc = struct.unpack_from("<I", d, co)[0]
        argv = struct.unpack_from("<Q", d, co + 8)[0]
        ao = va2off(argv)
        if ao is None or argc > 8:
            return base
        args = []
        for k in range(argc):
            tp = struct.unpack_from("<Q", d, ao + k * 8)[0]
            to = va2off(tp)
            if to is None:
                args.append("?")
            else:
                args.append(ctype_idx_from_ptr(to, depth + 1))
        return base + "<" + ",".join(args) + ">"
    if ty == 0x1D:
        o = va2off(data)
        if o is None:
            return "<arr>"
        return ctype_idx_from_ptr(o, depth + 1) + "[]"
    if ty == 0x14:
        ao = va2off(data)
        if ao is None:
            return "<arr2>"
        et = struct.unpack_from("<Q", d, ao)[0]
        rank = d[ao + 8]
        eo = va2off(et)
        inner = "?" if eo is None else ctype_idx_from_ptr(eo, depth + 1)
        return inner + "[" + "," * max(rank - 1, 0) + "]"
    if ty == 0x1E:
        return "!!%d" % data
    if ty == 0x0F:
        o = va2off(data)
        return ("?" if o is None else ctype_idx_from_ptr(o, depth + 1)) + "*"
    if ty == 0x10:
        o = va2off(data)
        return ("?" if o is None else ctype_idx_from_ptr(o, depth + 1)) + "&"
    if ty == 0x13:
        return "!%d" % data
    return PRIM.get(ty, "<ty%02X>" % ty)


def ctype_idx_from_ptr(off, depth):
    """off = 已定位的 Il2CTYPE 条目文件偏移"""
    data = struct.unpack_from("<Q", d, off)[0]
    ty = d[off + 10]
    if ty in (0x11, 0x12):
        return full(data) if data < NT else "<ty%02X>" % ty
    if ty == 0x1C:
        return "System.Object"
    if ty == 0x15:
        go = va2off(data)
        if go is None:
            return "<genptr>"
        base = full(struct.unpack_from("<I", d, go)[0])
        ci = struct.unpack_from("<Q", d, go + 8)[0]
        co = va2off(ci)
        if co is None:
            return base
        argc = struct.unpack_from("<I", d, co)[0]
        argv = struct.unpack_from("<Q", d, co + 8)[0]
        ao = va2off(argv)
        if ao is None or argc > 8:
            return base
        args = []
        for k in range(argc):
            tp = struct.unpack_from("<Q", d, ao + k * 8)[0]
            to = va2off(tp)
            args.append("?" if to is None else ctype_idx_from_ptr(to, depth + 1))
        return base + "<" + ",".join(args) + ">"
    if ty == 0x1D:
        o = va2off(data)
        return ("?" if o is None else ctype_idx_from_ptr(o, depth + 1)) + "[]"
    if ty == 0x14:
        ao = va2off(data)
        if ao is None:
            return "<arr2>"
        et = struct.unpack_from("<Q", d, ao)[0]
        rank = d[ao + 8]
        eo = va2off(et)
        inner = "?" if eo is None else ctype_idx_from_ptr(eo, depth + 1)
        return inner + "[" + "," * max(rank - 1, 0) + "]"
    if ty == 0x1E:
        return "!!%d" % data
    if ty == 0x0F:
        o = va2off(data)
        return ("?" if o is None else ctype_idx_from_ptr(o, depth + 1)) + "*"
    if ty == 0x10:
        o = va2off(data)
        return ("?" if o is None else ctype_idx_from_ptr(o, depth + 1)) + "&"
    if ty == 0x13:
        return "!%d" % data
    return PRIM.get(ty, "<ty%02X>" % ty)


# 每类型 fieldStart (+0x1C) 与 fieldCount (+0x4E)
S16 = [(SALT[i] & 0xFFFF) - 0x10000 if SALT[i] & 0x8000 else (SALT[i] & 0xFFFF) for i in range(NT)]
starts = {}
fcnt = {}
for rec in recs:
    i = rec["i"]
    v = ((rec["r7"] - rec["s"]) + 0xAA6F650E) & M32
    raw16 = struct.unpack_from("<H", BUF, T0 + i * STEP + 0x4E)[0]
    sr = raw16 - 0x10000 if raw16 & 0x8000 else raw16
    n = (sr - S16[i] - 2) & 0xFFFF
    fcnt[i] = n
    if v != M32:
        starts[i] = v

print("[字段] 有字段类型 = %d / %d" % (len(starts), NT))
sv = sorted(starts.values())
print("  start 范围 [%d, %d]  唯一值 %d" % (sv[0], sv[-1], len(set(sv))))
print("  字段总数(sum +0x4E) = %d" % sum(fcnt.values()))

# 差分交叉验证
order = sorted(starts.items(), key=lambda kv: kv[1])
ok = bad = 0
for k in range(len(order) - 1):
    ti, st = order[k]
    if order[k + 1][1] - st == fcnt[ti]:
        ok += 1
    else:
        bad += 1
print("  差分 vs +0x4E: 一致 %d / 不一致 %d  (%.2f%%)"
      % (ok, bad, 100.0 * ok / max(ok + bad, 1)))

# 输出
nlines = 0
with open(OUT, "w", encoding="utf-8") as f:
    f.write("# 字段表（v1）  类型索引\t类型全名\t字段索引\t字段名\t字段类型\n")
    f.write("# 表位置 abs=0x%X  记录 12 字节  prf(i)=((i*0x7740EEFF55F40540+0x49ED7F5AFCC4AF8)>>0x11)\n" % F0)
    f.write("# 字段总数 %d  有字段类型 %d\n\n" % (sum(fcnt.values()), len(starts)))
    for ti in sorted(starts):
        st = starts[ti]
        n = fcnt[ti]
        if n <= 0:
            continue
        f.write("\n## [%d] %s  (%d 字段)\n" % (ti, full(ti), n))
        for k in range(n):
            fi = st + k
            if F0 + fi * 0xC + 12 > FSIZE:
                break
            a, b, c = struct.unpack_from("<3I", BUF, F0 + fi * 0xC)
            pv = prf(fi)
            nid = ((c ^ 0x5DAAB140) - pv) & M32
            tidx = ((b - pv) - 0xF2A3D7F) & M32
            fn = dec(nid)
            f.write("    %-40s %s\n" % (fn if fn else "<bad %08X>" % nid, ctype(tidx)))
            nlines += 1

print("[+] %s  (%d 行字段)" % (OUT, nlines))

# 扁平 TSV
OUT_TSV = r"D:\Carol-start\_rea\bh3_fields.tsv"
with open(OUT_TSV, "w", encoding="utf-8") as f:
    f.write("typeIdx\ttypeName\tfieldIdx\tfieldName\tfieldType\n")
    for ti in sorted(starts):
        st = starts[ti]
        n = fcnt[ti]
        if n <= 0:
            continue
        tn = full(ti)
        for k in range(n):
            fi = st + k
            if F0 + fi * 0xC + 12 > FSIZE:
                break
            a, b, c = struct.unpack_from("<3I", BUF, F0 + fi * 0xC)
            pv = prf(fi)
            fn = dec(((c ^ 0x5DAAB140) - pv) & M32)
            f.write("%d\t%s\t%d\t%s\t%s\n"
                    % (ti, tn, fi, fn if fn else "", ctype(((b - pv) - 0xF2A3D7F) & M32)))
print("[+] %s" % OUT_TSV)

# 校验
print("\n[校验] 已知类型字段")
for t in ("System.String", "System.Int32", "System.Exception", "System.Object"):
    ti = next((r["i"] for r in recs if full(r["i"]) == t), None)
    if ti is None:
        print("  %s 未找到" % t)
        continue
    n = fcnt.get(ti, 0)
    names = []
    if n:
        st = starts[ti]
        for k in range(min(n, 10)):
            a, b, c = struct.unpack_from("<3I", BUF, F0 + (st + k) * 0xC)
            names.append(dec(((c ^ 0x5DAAB140) - prf(st + k)) & M32))
    print("  %-20s %2d 字段: %s" % (t, n, ", ".join(str(x) for x in names)))
