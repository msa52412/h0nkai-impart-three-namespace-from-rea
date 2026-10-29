#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证 0x242AC00 处 0x18 记录表是否为事件表（add/remove/raise/type/name/token）"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
T18 = 0x242AC00
LIM = 0x24AAC18          # 字符串池起点
N_MAX = (LIM - T18) // 0x18

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


BUF = open(META, "rb").read()
POOL = (struct.unpack_from("<I", d, va2off(0x188198E50))[0] ^ 0x7483FF7A) & M32
P = BASE + POOL
KM = (-0x394A88E12FFFF3A0) & M64
KA = 0x53DB1FC7E9ECC644
KS = 0x64C7CE0352814CF6
_u64 = struct.Struct("<Q")


def dec(pid):
    L = (pid >> 24) & 0xFF
    if L == 0:
        return None
    ix = pid & 0xFFFFFF
    src = P + ix
    nb = (L + 7) >> 3
    if src + nb * 8 > len(BUF):
        return None
    key = (ix * KM + KA) & M64
    out = bytearray()
    for b in range(nb):
        out += (_u64.unpack_from(BUF, src + b * 8)[0] ^ key).to_bytes(8, "little")
        key = (key + KS) & M64
    try:
        t = out[:L].decode("utf-8")
    except UnicodeDecodeError:
        return None
    for ch in t:
        if ord(ch) < 0x20 or ord(ch) == 0x7F:
            return None
    return t


def prf18(i):
    t = ((i * 0x7A00) ^ 0x3B79566A) & M64
    t = (t * 0x3EA7ABC3) & M64
    t = (t ^ 0x52121A98000) & M64
    t = t >> 0xC
    return (t & M32) * 0x20CF3F69 & M32


def rec(i):
    o = BASE + T18 + i * 0x18
    return struct.unpack_from("<6I", BUF, o)


print("可用记录上限 %d" % N_MAX)
print()
print("%-6s %-34s %-10s %-10s %-10s %-10s %s"
      % ("i", "name[4]", "add[0]", "remove[1]", "raise[2]", "type[3]", "tok[5]"))
ok = 0
fail_at = None
for i in range(0, 40):
    p0, p1, p2, p3, p4, p5 = rec(i)
    v = prf18(i)
    nm = dec((v ^ ((p4 + 0xBFC65639) & M32)) & M32)
    print("%-6d %-34s %-10X %-10X %-10X %-10d %08X"
          % (i, nm, (p0 ^ v), (p1 ^ v), (p2 ^ v), (p3 + 0xFCC28A65) & M32 ^ v,
             ((p5 + 0xCE2556FD) & M32) ^ v ^ 0x3081751A))
    if nm:
        ok += 1

# 连续有效长度
run = 0
best = 0
bestpos = 0
for i in range(N_MAX):
    p0, p1, p2, p3, p4, p5 = rec(i)
    v = prf18(i)
    nm = dec((v ^ ((p4 + 0xBFC65639) & M32)) & M32)
    if nm:
        run += 1
        if run > best:
            best = run
            bestpos = i - run + 1
    else:
        run = 0
print()
print("最长连续有效名字游程 = %d，起始索引 %d" % (best, bestpos))
