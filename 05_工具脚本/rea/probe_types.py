#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
探针：验证类型表 per-record salt 公式（来自 asm_42b910.txt 的 FUN_18042BD50）

  0x18042bd74  MOV RCX,0x1f17946ef935
  0x18042bd7e  MOV RAX,RBP           ; RBP = index
  0x18042bd81  IMUL RAX,RCX          ; index * 0x1F17946EF935
  0x18042bd85  IMUL RBX,RBP,0x5c     ; index * 0x5C
  0x18042bd89  MOV RCX,0xafd81baecafdac6
  0x18042bd93  ADD RAX,RCX
  0x18042bd9d  SHR RAX,0x15
  0x18042bdaf  ADD RAX,0x54760499
  0x18042bdb5  IMUL RDI,RAX,0x1125f1b6   ; salt
  0x18042bdc4  MOV EAX,[RBX+4]
  0x18042bdc2  SUB EAX,EDI
  0x18042bdce  CMP EAX,0xfbe4139        ; 有效性标记
"""
import struct

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
print("类型表 offset = 0x%X  条数 = %d" % (TYPE_OFF, N_TYPE))

with open(META, "rb") as f:
    BUF = f.read()
FSIZE = len(BUF)
T_ABS = BASE + TYPE_OFF
print("类型表绝对位置 = 0x%X  文件大小 = 0x%X" % (T_ABS, FSIZE))
print("理论占用 = 0x%X" % (N_TYPE * 0x5C))


def salt(i):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    x = (x * 0x1125F1B6) & M64
    return x & M32


print("\n[*] 逐条验证 [rec+4] - salt == 0xFBE4139")
hits = []
for i in range(min(N_TYPE, 3000)):
    off = T_ABS + i * 0x5C
    if off + 0x5C > FSIZE:
        break
    v = struct.unpack_from("<I", BUF, off + 4)[0]
    if ((v - salt(i)) & M32) == 0xFBE4139:
        hits.append(i)

print("前 3000 条命中: %d" % len(hits))
print("命中索引前 40: %s" % hits[:40])

if not hits:
    print("\n[!] 零命中，尝试变体")
    for name, fn in [
        ("不加 0x54760499", lambda i: (((i * 0x1F17946EF935 + 0xAFD81BAECAFDAC6) & M64) >> 0x15) * 0x1125F1B6 & M32),
        ("不截 32 位", lambda i: ((((i * 0x1F17946EF935 + 0xAFD81BAECAFDAC6) & M64) >> 0x15) + 0x54760499) * 0x1125F1B6 & M64),
    ]:
        h = 0
        for i in range(500):
            v = struct.unpack_from("<I", BUF, T_ABS + i * 0x5C + 4)[0]
            if ((v - fn(i)) & M32) == 0xFBE4139:
                h += 1
        print("  %-20s 命中 %d/500" % (name, h))
else:
    # 看这些命中的记录长什么样
    print("\n[*] 命中记录原始 23 个 dword")
    for i in hits[:6]:
        off = T_ABS + i * 0x5C
        raw = struct.unpack_from("<23I", BUF, off)
        print("  i=%-5d %s" % (i, " ".join("%08X" % x for x in raw)))
