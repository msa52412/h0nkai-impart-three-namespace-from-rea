#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
count 独立字段 vs start 差分 交叉验证 + methodStart C 修正 (0x2822B502)

u16 counts (来自 FUN_180430980 行 269-276):
  0x44 (i ^0x910A)  0x46 (n ^0x7883)  0x48 (m -(-0x1950))  0x4A (p -(-0x17A3))
  0x4C (e ^0x5BE4)  0x4E (? +2)       0x50 (v +0x27E6)     0x52 (? -(-0x1197))
starts:
  methodStart=+0x14 SUB 0x2822B502    nestedStart=+0x20 XOR 0x21FE571D
验证:
  A) method_count[0x48] 逐条 == methodStart 非空差分
  B) nested_count[0x46] 逐条 == nestedStart 差分
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
with open(META, "rb") as f:
    BUF = f.read()
T0 = BASE + TYPE_OFF

SALT = []
for i in range(NT):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    SALT.append(((x * 0x1125F1B6) & M64) & M32)

RAW = [struct.unpack_from("<23I", BUF, T0 + i * STEP) for i in range(NT)]
S16 = [(SALT[i] & 0xFFFF) - 0x10000 if SALT[i] & 0x8000 else (SALT[i] & 0xFFFF) for i in range(NT)]

# methodStart 修正 C
MS = [((RAW[i][5] - 0x2822B502) - SALT[i]) & M32 for i in range(NT)]
nz = [i for i in range(NT) if MS[i] != M32]
print("[methodStart C=0x2822B502]  -1=%d  非空=%d  值域=[%d, %d]"
      % (NT - len(nz), len(nz), min(MS[i] for i in nz), max(MS[i] for i in nz)))
mono = all(MS[nz[k + 1]] > MS[nz[k]] for k in range(len(nz) - 1))
print("  非空严格递增: %s" % mono)

# 差分 count
diff_cnt = {}
for k in range(len(nz) - 1):
    diff_cnt[nz[k]] = MS[nz[k + 1]] - MS[nz[k]]
diff_cnt[nz[-1]] = 408461 - MS[nz[-1]]
print("  差分总和 = %d (方法总数 408,461)" % sum(diff_cnt.values()))

# 独立 method_count (0x48)
mc48 = []
for i in range(NT):
    r = U16 = struct.unpack_from("<H", BUF, T0 + i * STEP + 0x48)[0]
    s16r = r - 0x10000 if r & 0x8000 else r
    mc48.append((s16r + 0x1950 - S16[i]) & 0xFFFF)
print("\n[method_count 0x48]  sum=%d  max=%d" % (sum(mc48), max(mc48)))

match = 0
mismatch = []
for i in range(NT):
    d = diff_cnt.get(i)
    if d is None:
        if mc48[i] == 0:
            match += 1
        else:
            mismatch.append((i, None, mc48[i]))
    else:
        if d == mc48[i]:
            match += 1
        else:
            mismatch.append((i, d, mc48[i]))
print("  与差分一致: %d/%d  不一致 %d" % (match, NT, len(mismatch)))
for i, d, m in mismatch[:8]:
    print("    i=%-6d 差分=%-6s 独立=%d" % (i, d, m))

# nested_count 0x46 vs nestedStart 差分
NS8 = [((RAW[i][8] ^ 0x21FE571D) - SALT[i]) & M32 for i in range(NT)]
nc46 = []
for i in range(NT):
    r = struct.unpack_from("<H", BUF, T0 + i * STEP + 0x46)[0]
    nc46.append(((r ^ 0x7883) - S16[i]) & 0xFFFF)
nz8 = [i for i in range(NT) if NS8[i] != M32]
diff8 = {}
for k in range(len(nz8) - 1):
    diff8[nz8[k]] = NS8[nz8[k + 1]] - NS8[nz8[k]]
diff8[nz8[-1]] = 21429 - NS8[nz8[-1]]
ok = bad = 0
for i in range(NT):
    d = diff8.get(i)
    if d == nc46[i]:
        ok += 1
    else:
        bad += 1
print("\n[nested 0x46 vs nestedStart 差分]  一致=%d 不一致=%d" % (ok, bad))

# 其它 count 与 start 的 sum 对照
print("\n[count↔start sum 对照]")
starts = {"methodStart+0x14": MS,
          "nestedStart+0x20": NS8,
          "propertyStart?+0x09": [((RAW[i][9] - 0x681DE620) - SALT[i]) & M32 for i in range(NT)],
          "eventStart?+0x07": [((RAW[i][7] - 0x55909AF2) - SALT[i]) & M32 for i in range(NT)],
          "vtableStart?+0x0F": [((RAW[i][15] - 0x2303AE63) - SALT[i]) & M32 for i in range(NT)],
          "ifOffStart?+0x15": [((RAW[i][21] - 0x19A9C75E) - SALT[i]) & M32 for i in range(NT)],
          "interStart+0x38": [((RAW[i][14] ^ 0x58833D25) - SALT[i]) & M32 for i in range(NT)],
          "generic?+0x04": [((RAW[i][4] ^ 0x35EFF672) - SALT[i]) & M32 for i in range(NT)]}
for n, v in starts.items():
    z = [x for x in v if x != M32]
    print("  %-20s max=%-9d -1数=%-7d" % (n, max(z) if z else -1, sum(1 for x in v if x == M32)))
