#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
类型表终局：全部字段解出 + 父类映射

新常量（来自 dec_str.c FUN_180430980）：
  +0x00 parentIndex    SUB 0x15F045CB  (Il2CTYPE 表)
  +0x04 elementIndex   SUB 0xFBE413A   (哨兵 0xFBE4139)
  +0x40 declaringType  XOR 0x5AEB04    (条件启用)
  +0x58 token          XOR 0x78647F39
  u16 counts:
  0x44 ^0x910A   0x46 ^0x7883(nested)   0x48 -0x1950(即+0xE6B0)
  0x4A -0x17A3(即+0xE85D)   0x4C ^0x5BE4   0x4E +2
  0x50 +0x27E6   0x52 -0x1197(即+0xEE69)
parentIndex 与 byvalTypeIndex(+0x28, SUB 0x67AD6F69) 同指 Il2CTYPE 表，
用 byval 反向映射即可得到 父类 TypeDefinition。
"""
import struct
from collections import Counter

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x5C
NT = 57487

with open(DLL, "rb") as f:
    dll = f.read()
e = struct.unpack_from("<I", dll, 0x3C)[0]
coff = e + 4
nsec = struct.unpack_from("<H", dll, coff + 2)[0]
optsz = struct.unpack_from("<H", dll, coff + 16)[0]
opt = coff + 20
IB = struct.unpack_from("<Q", dll, opt + 24)[0]
SECS = []
sh = opt + optsz
for i in range(nsec):
    o = sh + i * 40
    vs, va, rs, rp = struct.unpack_from("<IIII", dll, o + 8)
    SECS.append((va, vs, rs, rp))


def u32va(va):
    rva = va - IB
    for vaddr, vsize, rsize, rptr in SECS:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return None if rsize == 0 else struct.unpack_from("<I", dll, rptr + (rva - vaddr))[0]
    return None


TYPE_OFF = (u32va(0x188198E08) ^ 0x2B849DB3) & M32
POOL_OFF = u32va(0x188198E50) ^ 0x7483FF7A
K_MUL = (-0x394A88E12FFFF3A0) & M64
K_ADD = 0x53DB1FC7E9ECC644
K_STEP = 0x64C7CE0352814CF6

with open(META, "rb") as f:
    BUF = f.read()
FSIZE = len(BUF)
T0 = BASE + TYPE_OFF
P_ABS = BASE + POOL_OFF
_U64 = struct.Struct("<Q")

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
        out += (_U64.unpack_from(BUF, src + b * 8)[0] ^ key).to_bytes(8, "little")
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


RAW = [struct.unpack_from("<23I", BUF, T0 + i * STEP) for i in range(NT)]
U16 = {off: [struct.unpack_from("<H", BUF, T0 + i * STEP + off)[0] for i in range(NT)]
       for off in (0x44, 0x46, 0x48, 0x4A, 0x4C, 0x4E, 0x50, 0x52)}
S16 = [(SALT[i] & 0xFFFF) - (1 << 16) if SALT[i] & 0x8000 else (SALT[i] & 0xFFFF) for i in range(NT)]

NAME = [dec((((RAW[i][13] ^ 0x3399EFB) - SALT[i]) & M32)) for i in range(NT)]
NS = [dec(((((RAW[i][12] - SALT[i]) & M32) - 0x4B6ACCC7) & M32)) or "" for i in range(NT)]

# ---------- 1. 8 个 u16 count 求和 ----------
print("=" * 72)
print("[8 个 u16 count]  (nested 0x46 应 = 21429)")
cnts = {}
for off, C, isxor in [(0x44, 0x910A, 1), (0x46, 0x7883, 1), (0x48, -0x1950, 0),
                      (0x4A, -0x17A3, 0), (0x4C, 0x5BE4, 1), (0x4E, 2, 0),
                      (0x50, 0x27E6, 0), (0x52, -0x1197, 0)]:
    vals = []
    for i in range(NT):
        r = U16[off][i] - (1 << 16) if U16[off][i] & 0x8000 else U16[off][i]
        v = ((r ^ C) if isxor else (r - C)) - S16[i]
        vals.append(v & 0xFFFF)
    neg = sum(1 for v in vals if v > 0x7FFF)
    small = sum(1 for v in vals if v <= 200)
    print("  0x%02X: sum=%-9d max=%-7d 负值数(>0x7FFF)=%-6d ≤200 的=%d"
          % (off, sum(vals) & 0xFFFFFFFFFFFF, max(vals), neg, small))
    cnts[off] = vals

# ---------- 2. token ----------
print("\n[token] C=0x78647F39")
tok = [((RAW[i][22] ^ 0x78647F39) - SALT[i]) & M32 for i in range(NT)]
nz = [v for v in tok if v != M32]
hi = Counter(v >> 24 for v in nz)
print("  有效=%d uniq=%d  高字节分布=%s" % (len(nz), len(set(nz)), dict(hi.most_common(6))))
print("  前 6 token: %s" % [hex(v) for v in tok[:6]])

# ---------- 3. parent / byval ----------
print("\n[parentIndex pos=0 SUB 0x15F045CB]  [byval pos=10 SUB 0x67AD6F69]")
parent = [((RAW[i][0] - 0x15F045CB) - SALT[i]) & M32 for i in range(NT)]
byval = [((RAW[i][10] - 0x67AD6F69) - SALT[i]) & M32 for i in range(NT)]
print("  parent: -1=%d 有效=%d 值域=[%d, %d]"
      % (sum(1 for v in parent if v == M32), sum(1 for v in parent if v != M32),
         min(v for v in parent if v != M32), max(v for v in parent if v != M32)))
print("  byval : -1=%d 有效=%d 值域=[%d, %d] uniq=%d"
      % (sum(1 for v in byval if v == M32), sum(1 for v in byval if v != M32),
         min(v for v in byval if v != M32), max(v for v in byval if v != M32),
         len(set(v for v in byval if v != M32))))

# byval -> typedef 反向映射
rev = {}
for i in range(NT):
    if byval[i] != M32:
        rev.setdefault(byval[i], i)

hit = 0
miss = 0
PAR = []
for i in range(NT):
    p = parent[i]
    if p == M32:
        PAR.append(None)
        continue
    t = rev.get(p)
    PAR.append(t)
    if t is not None:
        hit += 1
    else:
        miss += 1
print("  parent→typedef: 命中=%d 未命中=%d" % (hit, miss))


def full(i):
    return (NS[i] + "." if NS[i] else "") + (NAME[i] or "?")


print("\n[父类验证]")
for t in ("System.String", "System.Exception", "System.Int32", "UnityEngine.GameObject",
          "MoleMole.BaseActor", "System.Object", "System.ValueType", "System.Enum"):
    ns, _, tn = t.rpartition(".")
    idx = next((i for i in range(NT) if NAME[i] == tn and NS[i] == ns), None)
    if idx is None:
        print("  %-28s 未找到" % t)
        continue
    p = PAR[idx]
    print("  %-28s -> %s" % (t, full(p) if p is not None else ("nil" if parent[idx] == M32 else "<idx %d 未知>" % parent[idx])))

# ---------- 4. 输出 ----------
OUT = r"D:\Carol-start\_rea\bh3_types_parents.txt"
with open(OUT, "w", encoding="utf-8") as f:
    f.write("index\ttype\tmethodStart\tmethodCount\tparent\tdeclaring\n")
    for i in range(NT):
        p = PAR[i]
        f.write("%d\t%s\t%d\t%s\n" % (i, full(i), parent[i], full(p) if p else ""))
print("\n[+] %s" % OUT)

print("\n[父类频次 Top 15]")
c = Counter(full(p) for p in PAR if p is not None)
for k, v in c.most_common(15):
    print("  %-40s %6d" % (k, v))
