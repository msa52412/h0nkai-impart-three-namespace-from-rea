#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""探针 2：验证类型记录的名字字段解密"""
import struct
from collections import Counter

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF

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
            if rsize == 0:
                return None
            return struct.unpack_from("<I", dll, rptr + (rva - vaddr))[0]
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


def salt(i):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    return ((x * 0x1125F1B6) & M64) & M32


def dec(pid):
    length = (pid >> 24) & 0xFF
    if length == 0:
        return ""
    if length > 0x100:
        return None
    index = pid & 0xFFFFFF
    src = P_ABS + index
    nb = (length + 7) >> 3
    if src + nb * 8 > FSIZE:
        return None
    key = (index * K_MUL + K_ADD) & M64
    out = bytearray()
    for b in range(nb):
        out += (_U64.unpack_from(BUF, src + b * 8)[0] ^ key).to_bytes(8, "little")
        key = (key + K_STEP) & M64
    try:
        s = out[:length].decode("utf-8")
    except UnicodeDecodeError:
        return None
    for ch in s:
        if ord(ch) < 0x20 or ord(ch) == 0x7F:
            return None
    return s


print("[*] 检查失败记录的 [rec+4]-salt 分布（前 500）")
cnt = Counter()
for i in range(500):
    v = struct.unpack_from("<I", BUF, T_ABS + i * 0x5C + 4)[0]
    cnt[("%08X" % ((v - salt(i)) & M32))] += 1
for k, n in cnt.most_common(8):
    print("    %s  x%d" % (k, n))

print("\n[*] 名字字段解密（i=0..40）")
print("%-5s %-10s %-10s %-28s %-28s" % ("i", "f30^? ", "f34^?", "A = dec(f34^0x3399EFB-s)", "B = dec(f30-s-0x4B6ACCC7)"))
okA = okB = 0
for i in range(41):
    off = T_ABS + i * 0x5C
    f30, f34 = struct.unpack_from("<II", BUF, off + 0x30)
    s = salt(i)
    a = dec(((f34 ^ 0x3399EFB) - s) & M32)
    b = dec((((f30 - s) & M32) - 0x4B6ACCC7) & M32)
    okA += a is not None
    okB += b is not None
    print("%-5d %-10X %-10X %-28s %-28s" % (i, f30, f34, (a or "-")[:28], (b or "-")[:28]))

print("\n前 41 条: A 成功 %d, B 成功 %d" % (okA, okB))
