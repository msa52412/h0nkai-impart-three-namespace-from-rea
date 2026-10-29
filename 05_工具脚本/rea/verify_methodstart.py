#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证 +0x20 = methodStart（XOR 0x21FE571D 变换）
     +0x46 = methodCount (u16, XOR 0x7883)

依据 asm_42b910.txt:
  18042b945  MOVZX EAX,word ptr [R8 + 0x46]
  18042b94a  MOV R12D,0x7883
  18042b950  XOR AX,R12W
  18042b954  SUB AX,word ptr [RDX]        ; - (u16)salt
  18042b961  MOV ECX,dword ptr [R8 + 0x20]
  18042b965  XOR ECX,0x21fe571d
  18042b96b  SUB ECX,dword ptr [RDI]      ; - (int)salt
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
IDXARR_OFF = (u32va(0x188198E6C) - 0x3670DF73) & M32
K_MUL = (-0x394A88E12FFFF3A0) & M64
K_ADD = 0x53DB1FC7E9ECC644
K_STEP = 0x64C7CE0352814CF6

with open(META, "rb") as f:
    BUF = f.read()
FSIZE = len(BUF)
T_ABS = BASE + TYPE_OFF
P_ABS = BASE + POOL_OFF
I_ABS = BASE + IDXARR_OFF
_U64 = struct.Struct("<Q")
print("类型表 0x%X  池 0x%X  索引数组 0x%X" % (T_ABS, P_ABS, I_ABS))

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


MS, MC, NAME, NS = [], [], [], []
for i in range(NT):
    off = T_ABS + i * STEP
    d = struct.unpack_from("<23I", BUF, off)
    s = SALT[i]
    ms = (((d[8] ^ 0x21FE571D) - s) & M32)
    lo16 = struct.unpack_from("<H", BUF, off + 0x46)[0]
    mc = ((lo16 ^ 0x7883) - (s & 0xFFFF)) & 0xFFFF
    MS.append(ms)
    MC.append(mc)
    NAME.append(dec((((d[13] ^ 0x3399EFB) - s) & M32)))
    NS.append(dec(((((d[12] - s) & M32) - 0x4B6ACCC7) & M32)) or "")

print("\n[*] methodStart[0..15] = %s" % MS[:16])
print("    methodCount[0..15] = %s" % MC[:16])
print("    sum(count) = %d   (真实方法数 %d)" % (sum(MC), N_METHOD))
print("    max(start) = %d" % max(MS))
print("    单调递减处 = %d" % sum(1 for i in range(NT - 1) if MS[i + 1] < MS[i]))
print("    start+count 越界 = %d" % sum(1 for i in range(NT) if MS[i] + MC[i] > N_METHOD))

# 覆盖检查：所有 [start, start+count) 是否恰好铺满 0..408461
cover = [0] * (N_METHOD + 2)
for i in range(NT):
    for k in range(MS[i], min(MS[i] + MC[i], N_METHOD)):
        cover[k] += 1
print("    覆盖: 0 次=%d  1 次=%d  多次=%d"
      % (sum(1 for x in cover[:N_METHOD] if x == 0),
         sum(1 for x in cover[:N_METHOD] if x == 1),
         sum(1 for x in cover[:N_METHOD] if x > 1)))

print("\n[*] 前 8 个类型 + 方法范围")
for i in range(8):
    print("    %-5d %-30s %-22s start=%-7d count=%-4d"
          % (i, (NS[i] + "." + (NAME[i] or "?"))[:30], (NAME[i] or "?")[:22], MS[i], MC[i]))

print("\n[*] 索引数组 I_ABS 前 20 个 int32")
print("   ", [struct.unpack_from("<i", BUF, I_ABS + k * 4)[0] for k in range(20)])

print("\n[*] 类型 0 的方法索引（按 42B910 逻辑：idx = [rec+0x20]^0x21fe571d - salt + k）")
for i in (0, 1, 4):
    off = T_ABS + i * STEP
    d8 = struct.unpack_from("<I", BUF, off + 8)[0]
    base_idx = ((d8 ^ 0x21FE571D) - SALT[i]) & M32
    vals = [struct.unpack_from("<i", BUF, I_ABS + (base_idx + k) * 4)[0] for k in range(min(MC[i], 10))]
    print("    类型 %d (%s) base_idx=%d -> %s" % (i, NAME[i], base_idx, vals))
