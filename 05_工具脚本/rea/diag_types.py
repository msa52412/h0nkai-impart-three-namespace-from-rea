#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""诊断：为什么只有 28% 的类型记录能解出名字"""
import struct
from collections import Counter

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x5C

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
N_TYPE = (u32va(0x1881A3630) ^ 0x421DD17C) & M32
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
print("池 0x%X, 池可用到文件尾 = 0x%X" % (P_ABS, FSIZE - P_ABS))


def salt(i):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    return ((x * 0x1125F1B6) & M64) & M32


def dec(pid):
    length = (pid >> 24) & 0xFF
    if length == 0:
        return "", "len0"
    if length > 0x80:
        return None, "len>128(0x%X)" % length
    index = pid & 0xFFFFFF
    src = P_ABS + index
    nb = (length + 7) >> 3
    if src + nb * 8 > FSIZE:
        return None, "oob(idx=0x%X)" % index
    key = (index * K_MUL + K_ADD) & M64
    out = bytearray()
    for b in range(nb):
        out += (_U64.unpack_from(BUF, src + b * 8)[0] ^ key).to_bytes(8, "little")
        key = (key + K_STEP) & M64
    try:
        t = out[:length].decode("utf-8")
    except UnicodeDecodeError:
        return None, "utf8"
    for ch in t:
        if ord(ch) < 0x20 or ord(ch) == 0x7F:
            return None, "ctrl"
    return t, "ok"


okflag = []
reason = Counter()
for i in range(N_TYPE):
    off = T_ABS + i * STEP
    r13 = struct.unpack_from("<I", BUF, off + 0x34)[0]
    pid = ((r13 ^ 0x3399EFB) - salt(i)) & M32
    s, why = dec(pid)
    reason[why] += 1
    okflag.append(1 if why == "ok" else 0)

print("\n失败原因分布:")
for k, v in reason.most_common():
    print("  %-16s %d" % (k, v))

# 成功索引的连续性
print("\n成功索引分布（每 5000 一桶）:")
for b in range(0, N_TYPE, 5000):
    seg = okflag[b:b + 5000]
    print("  %6d-%6d  %4d/%4d  %5.1f%%" % (b, b + len(seg) - 1, sum(seg), len(seg),
                                            100.0 * sum(seg) / len(seg)))

# 找第一段连续成功
first_break = None
for i in range(N_TYPE):
    if not okflag[i]:
        first_break = i
        break
print("\n第一个失败索引 = %s" % first_break)

# 看失败点前后
if first_break is not None:
    for i in range(max(0, first_break - 3), min(N_TYPE, first_break + 6)):
        off = T_ABS + i * STEP
        raw = struct.unpack_from("<23I", BUF, off)
        print("  i=%-6d ok=%d  [4]-salt=%08X  r12=%08X r13=%08X"
              % (i, okflag[i], ((raw[1] - salt(i)) & M32), raw[12], raw[13]))
