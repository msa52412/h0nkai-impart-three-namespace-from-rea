#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""泛型形参表 + 泛型容器表（全量解出，2772 / 1967 条）

来源 FUN_18042fe20（VAR/MVAR 类型节点构建器，802 字节反编译）：

  形参表   base = buf + (u32(DAT_188198E40) - 0x77870E75) = buf + 0x01C1F458, 0x10/条, 2772 条
  容器表   base = buf + (u32(DAT_188198E00) ^ 0x7497C9EE) = buf + 0x0055C604, 0x10/条, 1967 条

  salt(i)  = ((i * 0x34D04BA0E4DB + 0xA13EE8C44CC682A) ^ 0x43427E7D) + 0x10776301   (64 位)
  nameId   = ((i32)rec[+0x04] + 0xEE50A144) ^ (uint32)salt(i)          → FUN_18043ab50
  container= (uint32)salt(i) ^ rec[+0x00] ^ 0x6FE8EE1B                 (-1 = 无宿主)

  prfC(c)  = ((uint)((((c*0x6AE9 ^ 0x2E6F3E3D) * 0x2AD3DD28) >> 0x16) * 0x4C39B37D >> 10)
              ^ 0x4DFAA6B0) * 0x22449C6E              (int32)
  flag     = (crec[+0x0C] - 0x175A3FDF) - prfC(c)     ∈ {0, 1}
             1 = MVAR（方法泛型），0 = VAR（类型泛型）
  owner    = (crec[+0x04] - 0x1DF344F8 - (prfC(c)+flag)) & 0xFFFFFFFF
             类型容器 → 类型索引；方法容器 → 方法索引
"""
import struct
import collections

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
OUT = r"D:\Carol-start\_rea\bh3_generic_params.tsv"

BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
NT = 57487
NM = 408458
NGP = 2772

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
POOL = BASE + (u32va(0x188198E50) ^ 0x7483FF7A)
T0 = BASE + ((u32va(0x188198E08) ^ 0x2B849DB3) & M32)
GP = BASE + ((u32va(0x188198E40) - 0x77870E75) & M32)
OWN = BASE + ((u32va(0x188198E00) ^ 0x7497C9EE) & M32)
STEP = 0x5C
NCT = 1967

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
    src = POOL + ix
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


TSALT = []
for i in range(NT):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    TSALT.append(((x * 0x1125F1B6) & M64) & M32)
TNAME = []
for i in range(NT):
    r = struct.unpack_from("<23I", BUF, T0 + i * STEP)
    s = TSALT[i]
    nm = dec((((r[13] ^ 0x3399EFB) - s) & M32))
    ns = dec(((((r[12] - s) & M32) - 0x4B6ACCC7) & M32)) or ""
    TNAME.append((ns + "." if ns else "") + (nm or "?"))


def prf_c(c):
    x = ((c * 0x6AE9) ^ 0x2E6F3E3D) & M64
    x = (x * 0x2AD3DD28) & M64
    x = (x >> 0x16) * 0x4C39B37D
    x = (x >> 10) & M32
    x ^= 0x4DFAA6B0
    return (x * 0x22449C6E) & M32


def salt(i):
    return ((((i * 0x34D04BA0E4DB + 0xA13EE8C44CC682A) & M64) ^ 0x43427E7D) + 0x10776301) & M64


# ---- 容器表 ----
CONT = {}
for c in range(NCT):
    d4, d12 = struct.unpack_from("<I", BUF, OWN + c * 0x10 + 4)[0], struct.unpack_from("<I", BUF, OWN + c * 0x10 + 0xC)[0]
    p = prf_c(c)
    flag = ((d12 - 0x175A3FDF) & M32) - p
    flag &= M32
    assert flag in (0, 1), (c, flag)
    owner = (d4 - 0x1DF344F8 - (p + flag)) & M32
    CONT[c] = (flag, owner)

# ---- 形参表 ----
GPN = []          # index -> name
GP_C = []         # index -> container
for i in range(NGP):
    r0, r1 = struct.unpack_from("<2I", BUF, GP + i * 0x10)
    s32 = salt(i) & M32
    nm = dec((((r1 + 0xEE50A144) & M32) ^ s32))
    GPN.append(nm or "")
    GP_C.append((s32 ^ r0 ^ 0x6FE8EE1B) & M32)

print("[*] 形参表 0x%08X  %d 条   容器表 0x%08X  %d 条"
      % (GP - BASE, NGP, OWN - BASE, NCT))
print("    空名 = %d" % sum(1 for x in GPN if not x))
print("    容器 -> 形参数 分组连续 = %s"
      % all(sorted(ps) == list(range(min(ps), min(ps) + len(ps)))
            for ps in [v for v in
                       [[j for j in range(NGP) if GP_C[j] == c] for c in range(NCT)]]))
nmeth = sum(1 for c in range(NCT) if CONT[c][0] == 1)
print("    方法容器 = %d   类型容器 = %d" % (nmeth, NCT - nmeth))
print("    类型容器 owner 越界 = %d   方法容器 owner 越界 = %d"
      % (sum(1 for c in range(NCT) if CONT[c][0] == 0 and CONT[c][1] >= NT),
         sum(1 for c in range(NCT) if CONT[c][0] == 1 and CONT[c][1] >= NM)))

print()
print("== 名字分布 top15 ==")
for k, v in collections.Counter(GPN).most_common(15):
    print("  %-18s %d" % (k or "<空>", v))

print()
print("== 抽样 ==")
for i in (0, 1, 2, 3, 26, 27, 100, 500, 1500, 2771):
    c = GP_C[i]
    flag, owner = (CONT[c] if c in CONT else (None, None))
    who = ("method#%d" % owner) if flag else (TNAME[owner] if owner is not None and owner < NT else "?")
    print("  %4d  %-16s  %-4s  %s" % (i, GPN[i], "MVAR" if flag else "VAR" if flag == 0 else "?", who))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("idx\tname\tcontainer\tkind\townerIdx\towner\n")
    for i in range(NGP):
        c = GP_C[i]
        flag, owner = CONT.get(c, (None, None))
        kind = "-" if flag is None else ("MVAR" if flag else "VAR")
        who = ""
        if owner is not None:
            who = ("method#%d" % owner) if flag else (TNAME[owner] if owner < NT else "?")
        f.write("%d\t%s\t%d\t%s\t%s\t%s\n" % (i, GPN[i], c, kind, "" if owner is None else owner, who))
print()
print("[+] 写出 %s" % OUT)
