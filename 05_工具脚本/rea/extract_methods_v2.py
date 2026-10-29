#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
方法表全量提取（含签名）

表基址 = buf + (u32(DAT_188198E58) - 0x17A3B99) = 0xFA8318, 记录 0x20, 共 408,458 条
PRF   = prf32(i)（64 位乘法链，反编译 FUN_18044c400 / FUN_18044beb0 取得）

记录布局（全部经反汇编/反编译双向核对）：
  +0x00 declaringType     (v + 0xE5AF14B4) ^ prf    Il2CType 索引
  +0x04 parameterStart    (v + 0xEA530370) ^ prf    -1 = 无参数
  +0x08 returnType        (v + 0xAEAE5FEE) ^ prf    0xFFFFFFFF = void
  +0x0C name              v ^ prf ^ 0x1D64B276      StringIndex
  +0x10 genericContainer  v ^ prf ^ 0x1A57A870      -1 = 非泛型方法
  +0x14 token             (v + 0xBD6FC398) ^ prf    0x06xxxxxx (MethodDef)
  +0x18 slot        u16   (v + 0xAC47) ^ prf16      0xFFFF = 非虚方法
  +0x1A paramCount  u16   (v + 0x2641) ^ prf16      合计 351,719
  +0x1C flags       u16   (v + 0xDAB0) ^ prf16      MethodAttributes
  +0x1E iflags      u16   v ^ prf16 ^ 0x4D12        MethodImplAttributes

参数表基址 = 0xAC0F38, 记录 0xC, 351,719 条：
  [0] typeIndex  (v + 0xC6F108A2) ^ prf3
  [4] nameIndex  v ^ 0x4CC553B0 ^ prf3
  [8] token      v ^ 0x6697D2D9 ^ prf3   0x08xxxxxx (Param)
  prf3(i) = ((i*0x90C17665DF3 + 0x125F81CCD2DF4209) ^ 0x390ACBF7) * 0x7BABB4A2 >> 0xF) + 0x476926E5
"""
import struct
import sys

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
OUT = r"D:\Carol-start\_rea\bh3_methods_v2.tsv"
OUT_SIG = r"D:\Carol-start\_rea\bh3_method_sigs.txt"

BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x5C
NT = 57487
NCTYPE = 354184
TBL = 0xFA8318
N = 408458
PARAM = 0xAC0F38
NPARAM = 351719

# ---------------- PE ----------------
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
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((va, vs, rs, rp))


def va2off(va):
    rva = va - IB
    for vaddr, vsize, rsize, rptr in SECS:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return None if rsize == 0 else rptr + (rva - vaddr)
    return None


def u32va(va):
    o = va2off(va)
    return None if o is None else struct.unpack_from("<I", d, o)[0]


BUF = open(META, "rb").read()
CT = va2off(0x186D41F80)
POOL = u32va(0x188198E50) ^ 0x7483FF7A
P = BASE + POOL
TYPE_OFF = (u32va(0x188198E08) ^ 0x2B849DB3) & M32
T0 = BASE + TYPE_OFF
KM = (-0x394A88E12FFFF3A0) & M64
KA = 0x53DB1FC7E9ECC644
KS = 0x64C7CE0352814CF6
_u64 = struct.Struct("<Q")
_sc = {}


def dec(pid):
    s = _sc.get(pid, 0)
    if s != 0:
        return s
    L = (pid >> 24) & 0xFF
    if L == 0:
        _sc[pid] = ""
        return ""
    ix = pid & 0xFFFFFF
    src = P + ix
    nb = (L + 7) >> 3
    if src + nb * 8 > len(BUF):
        _sc[pid] = None
        return None
    key = (ix * KM + KA) & M64
    out = bytearray()
    for b in range(nb):
        out += (_u64.unpack_from(BUF, src + b * 8)[0] ^ key).to_bytes(8, "little")
        key = (key + KS) & M64
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


# ---------------- 类型表（name/ns） ----------------
TSALT = []
for i in range(NT):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    TSALT.append(((x * 0x1125F1B6) & M64) & M32)

TNAME = []
for i in range(NT):
    off = T0 + i * STEP
    r = struct.unpack_from("<23I", BUF, off)
    s = TSALT[i]
    nm = dec((((r[13] ^ 0x3399EFB) - s) & M32))
    ns = dec(((((r[12] - s) & M32) - 0x4B6ACCC7) & M32)) or ""
    TNAME.append((ns + "." if ns else "") + (nm or "?"))

PRIM = {0x01: "void", 0x02: "bool", 0x03: "char", 0x04: "sbyte", 0x05: "byte",
        0x06: "short", 0x07: "ushort", 0x08: "int", 0x09: "uint", 0x0A: "long",
        0x0B: "ulong", 0x0C: "float", 0x0D: "double", 0x0E: "string", 0x16: "TypedReference",
        0x18: "IntPtr", 0x19: "UIntPtr", 0x1C: "object"}

# ---------------- 泛型形参名表（0x1C1F458, 0x10/条, 2772 条, 见 extract_generic_params.py） ----------------
GP = BASE + ((u32va(0x188198E40) - 0x77870E75) & M32)
NGPN = 2772
GPN = []
for _i in range(NGPN):
    _s = ((((_i * 0x34D04BA0E4DB + 0xA13EE8C44CC682A) & M64) ^ 0x43427E7D) + 0x10776301) & M64
    _r1 = struct.unpack_from("<I", BUF, GP + _i * 0x10 + 4)[0]
    GPN.append(dec((((_r1 + 0xEE50A144) & M32) ^ (_s & M32))) or ("T%d" % _i))
print("[*] 泛型形参名 %d 条（0x%08X）" % (NGPN, GP - BASE))



def ctype_po(idx):
    """Il2CType 索引 -> 条目文件偏移"""
    if idx == M32 or idx >= NCTYPE:
        return None
    p = struct.unpack_from("<Q", d, CT + idx * 8)[0]
    return va2off(p)


def tn(idx, depth=0):
    po = ctype_po(idx)
    return "?" if po is None else tn_by_po(po, depth)


def tn_by_po(po, depth=0):
    """按文件偏移解析 Il2CType（data 域视类型码解释为指针或索引）"""
    if po is None or po + 11 > len(d) or depth > 6:
        return "?"
    ty = d[po + 10]
    data = struct.unpack_from("<Q", d, po)[0]
    if ty in (0x11, 0x12):
        return TNAME[data] if data < NT else "?"
    if ty == 0x0F:                                  # PTR
        return tn_by_po(va2off(data), depth + 1) + "*"
    if ty == 0x10:                                  # BYREF
        return "ref " + tn_by_po(va2off(data), depth + 1)
    if ty == 0x1D:                                  # SZARRAY -> etype 指针
        return tn_by_po(va2off(data), depth + 1) + "[]"
    if ty == 0x14:                                  # ARRAY -> Il2CppArrayType{etype,rank,...}
        ao = va2off(data)
        if ao is None:
            return "[,]"
        return tn_by_po(va2off(struct.unpack_from("<Q", d, ao)[0]), depth + 1) + "[,]"
    if ty == 0x15:                                  # GENERICINST -> Il2CppGenericClass
        go = va2off(data)
        if go is None or go + 16 > len(d):
            return "?"
        bi = struct.unpack_from("<i", d, go)[0]
        ci = struct.unpack_from("<Q", d, go + 8)[0]     # class_inst
        base = TNAME[bi] if 0 <= bi < NT else "?"
        co = va2off(ci)
        if co is None:
            return base + "<...>"
        argc = struct.unpack_from("<I", d, co)[0]
        argv = struct.unpack_from("<Q", d, co + 8)[0]
        ao = va2off(argv)
        args = []
        for k in range(min(argc, 8)):
            if ao is None or ao + k * 8 + 8 > len(d):
                args.append("?")
                continue
            args.append(tn_by_po(va2off(struct.unpack_from("<Q", d, ao + k * 8)[0]), depth + 1))
        return "%s<%s>" % (base, ",".join(args))
    if ty == 0x13:
        return GPN[data] if data < NGPN else "T%d" % data
    if ty == 0x1E:
        return GPN[data] if data < NGPN else "M%d" % data
    return PRIM.get(ty, "ty%02X" % ty)


# ---------------- 参数 ----------------
P3 = []
for i in range(NPARAM):
    t = (i * 0x90C17665DF3 + 0x125F81CCD2DF4209) & M64
    t ^= 0x390ACBF7
    t = (t * 0x7BABB4A2) & M64
    P3.append(((t >> 0xF) + 0x476926E5) & M32)

PNAME = [None] * NPARAM
PTYPE = [None] * NPARAM
PTOK = [None] * NPARAM


def load_param(k):
    if PNAME[k] is not None:
        return
    r = struct.unpack_from("<3I", BUF, BASE + PARAM + k * 0xC)
    p = P3[k]
    PTYPE[k] = ((r[0] + 0xC6F108A2) & M32) ^ p
    PNAME[k] = dec(((r[1] ^ 0x4CC553B0) ^ p) & M32) or ""
    PTOK[k] = ((r[2] ^ 0x6697D2D9) ^ p) & M32


# ---------------- 主循环 ----------------
PRF = []
for i in range(N):
    x = ((i * 0xB069) ^ 0x3E382F2D) & M64
    x = (x * 0x24147491) & M64
    x = (x ^ 0xF997B4A800) >> 10
    x = (x * 0x3857AACA) & M64
    PRF.append((x >> 0xE) & M32)

rows = []
bad_name = 0
bad_decl = 0
for i in range(N):
    o = BASE + TBL + i * 0x20
    r = struct.unpack_from("<8I", BUF, o)
    p = PRF[i]
    p16 = p & 0xFFFF
    nm = dec(((r[3] ^ p) ^ 0x1D64B276) & M32)
    if not nm:
        bad_name += 1
        nm = "?"
    decl = ((r[0] + 0xE5AF14B4) & M32) ^ p
    if decl >= NT:
        bad_decl += 1
    rt = ((r[2] + 0xAEAE5FEE) & M32) ^ p
    tok = ((r[5] + 0xBD6FC398) & M32) ^ p
    ps = ((r[1] + 0xEA530370) & M32) ^ p
    gc = ((r[4] ^ p) ^ 0x1A57A870) & M32
    slot = ((struct.unpack_from("<H", BUF, o + 0x18)[0] + 0xAC47) & 0xFFFF) ^ p16
    pc = ((struct.unpack_from("<H", BUF, o + 0x1A)[0] + 0x2641) & 0xFFFF) ^ p16
    fl = ((struct.unpack_from("<H", BUF, o + 0x1C)[0] + 0xDAB0) & 0xFFFF) ^ p16
    ifl = (struct.unpack_from("<H", BUF, o + 0x1E)[0] ^ p16 ^ 0x4D12) & 0xFFFF
    params = []
    if pc and ps != M32:
        for k in range(ps, ps + pc):
            if k >= NPARAM:
                break
            load_param(k)
            params.append("%s %s" % (tn(PTYPE[k]), PNAME[k] or ("arg%d" % (k - ps))))
    rows.append((i, "%08X" % tok, decl, TNAME[decl] if decl < NT else "?",
                 nm, tn(rt), "%04X" % fl, "0xFFFF" if slot == 0xFFFF else slot,
                 "%04X" % ifl, pc, "" if gc == M32 else gc,
                 ", ".join(params)))

print("记录 %d 条，空名 %d，声明类型越界 %d" % (len(rows), bad_name, bad_decl))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("idx\ttoken\tdeclTypeIdx\tdeclType\tname\treturnType\tflags\tslot\tiflags\tparamCount\tgenericContainer\tparams\n")
    for r in rows:
        f.write("\t".join(str(x) for x in r) + "\n")
print("[+] %s" % OUT)

# 签名视图
with open(OUT_SIG, "w", encoding="utf-8") as f:
    for r in rows:
        f.write("%s %s::%s(%s)  // tok=%s flags=%s slot=%s gc=%s\n"
                % (r[5], r[3], r[4], r[11], r[1], r[6], r[7], r[10]))
print("[+] %s" % OUT_SIG)

# 校验
print("\n[校验] 已知方法签名")
want = [("System.String", "IndexOf"), ("System.String", "Substring"),
        ("UnityEngine.Transform", "SetPositionAndRotation"),
        ("System.Collections.Generic.List`1", "Add")]
for t, m in want:
    for r in rows:
        if r[3] == t and r[4] == m:
            print("  %s %s::%s(%s)" % (r[5], r[3], r[4], r[11]))
            break
