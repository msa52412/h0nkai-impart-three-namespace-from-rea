#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
类型表 → 方法/字段归属关联，并用枚举自洽性验证字段位置

假设：
  pos=5   methodStart   (max 408452, 方法总数 408461)
  pos=10  fieldStart    (max 142514)
  pos=0/1 byvalTypeIndex / byrefTypeIndex (max ~351.8k)
  pos=21  常量 3055 -> flags?
count 用 start 差分求得，不依赖 count 字段位置
"""
import struct
from collections import Counter, defaultdict

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x5C
NT = 57487
N_METHOD = 408461

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
T_ABS = BASE + TYPE_OFF
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
    length = (pid >> 24) & 0xFF
    if length == 0 or length > 0x80:
        _sc[pid] = None
        return None
    index = pid & 0xFFFFFF
    src = P_ABS + index
    nb = (length + 7) >> 3
    if src + nb * 8 > FSIZE:
        _sc[pid] = None
        return None
    key = (index * K_MUL + K_ADD) & M64
    out = bytearray()
    for b in range(nb):
        out += (_U64.unpack_from(BUF, src + b * 8)[0] ^ key).to_bytes(8, "little")
        key = (key + K_STEP) & M64
    try:
        t = out[:length].decode("utf-8")
    except UnicodeDecodeError:
        _sc[pid] = None
        return None
    for ch in t:
        if ord(ch) < 0x20 or ord(ch) == 0x7F:
            _sc[pid] = None
            return None
    _sc[pid] = t
    return t


REC = [struct.unpack_from("<23I", BUF, T_ABS + i * STEP) for i in range(NT)]
V = [[((REC[i][p] - SALT[i]) & M32) for p in range(23)] for i in range(NT)]
BASEV = [min(V[i][p] for i in range(NT)) for p in range(23)]
D = [[V[i][p] - BASEV[p] for p in range(23)] for i in range(NT)]

# name / namespace
NAME = [dec((((REC[i][13] ^ 0x3399EFB) - SALT[i]) & M32)) for i in range(NT)]
NS = [dec(((((REC[i][12] - SALT[i]) & M32) - 0x4B6ACCC7) & M32)) or "" for i in range(NT)]

MS = [D[i][5] for i in range(NT)]
FS = [D[i][10] for i in range(NT)]


def diff_counts(start, total):
    """由 start 数组求每条 count，最后一条用 total 补齐"""
    out = []
    for i in range(NT - 1):
        c = start[i + 1] - start[i]
        out.append(c if c >= 0 else 0)
    out.append(max(0, total - start[-1]))
    return out


MC = diff_counts(MS, N_METHOD)
print("methodStart 差分: sum=%d  负值数=%d  最后一条 count=%d"
      % (sum(MC), sum(1 for i in range(NT - 1) if MS[i + 1] < MS[i]), MC[-1]))
print("methodStart[0..8] = %s" % MS[:9])
print("method count 前 12 = %s" % MC[:12])
print("method count 分布: max=%d, =0 的有 %d 条, >100 的有 %d 条"
      % (max(MC), sum(1 for c in MC if c == 0), sum(1 for c in MC if c > 100)))

print("\n[*] 枚举自洽性验证：fieldStart 差分是否等于枚举值个数")
for tname in ("CmdId", "Retcode", "State"):
    idxs = [i for i in range(NT) if NAME[i] == tname]
    print("  %-10s 出现 %d 次" % (tname, len(idxs)))
    for i in idxs[:5]:
        fc = (FS[i + 1] - FS[i]) if i + 1 < NT else -1
        mc = MC[i]
        print("    i=%-6d ns=%-22s fieldStart=%-8d fieldCount=%-7d methodCount=%d"
              % (i, NS[i][:22], FS[i], fc, mc))

print("\n[*] 字段总数（fieldStart 差分）= %d" % sum(
    (FS[i + 1] - FS[i]) if FS[i + 1] >= FS[i] else 0 for i in range(NT - 1)) + (FS[-1] - FS[-1]))

print("\n[*] 用方法名反验：<Module> 类型的方法")
for i in range(NT):
    if NAME[i] == "<Module>":
        print("    i=%-6d ns=%-20s methodStart=%-7d count=%d" % (i, NS[i][:20], MS[i], MC[i]))
        if i > 4000:
            break

print("\n[*] 位置 21 是否为 flags（值分布）")
c = Counter(D[i][21] for i in range(NT))
for k, v in c.most_common(12):
    print("    0x%X (%d)  x%d" % (k, k, v))
