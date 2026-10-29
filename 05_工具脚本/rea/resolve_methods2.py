#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正：DAT_188198e88 / DAT_188198e98 是 8 字节全局。

伪代码 dec_str.c:1269-1270:
  lVar9 = (DAT_188198e98 + -0x56ca4fe4) + s_GlobalMetadata;
  uVar7 = (longlong)(int)((ulonglong)(longlong)DAT_188198e88 >> 3) ^ 0xd9bea51;
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


def rd(va, width):
    rva = va - IB
    for vaddr, vsize, rsize, rptr in SECS:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            if rsize == 0:
                return None
            off = rptr + (rva - vaddr)
            if width == 8:
                return struct.unpack_from("<Q", dll, off)[0]
            return struct.unpack_from("<I", dll, off)[0]
    return None


with open(META, "rb") as f:
    BUF = f.read()
FSIZE = len(BUF)

print("=" * 74)
print("同一地址按 4 / 8 字节读的对比")
print("=" * 74)
for va, name in [(0x188198E98, "DAT_188198e98"), (0x188198E88, "DAT_188198e88"),
                 (0x188198E84, "DAT_188198e84"), (0x188198E40, "DAT_188198e40")]:
    v4 = rd(va, 4)
    v8 = rd(va, 8)
    print("%s  4B=0x%08X  8B=0x%016X" % (name, v4, v8))

print()
print("=" * 74)
print("按 8 字节重算")
print("=" * 74)

X98 = rd(0x188198E98, 8)
X88 = rd(0x188198E88, 8)

tbl = (X98 - 0x56CA4FE4) & M64
count = ((X88 >> 3) & M32) ^ 0xD9BEA51

print("表偏移 = 0x%X - 0x56CA4FE4 = 0x%X (%d)" % (X98, tbl, tbl))
print("条数   = (0x%X >> 3) ^ 0xD9BEA51 = %d (0x%X)" % (X88, count, count))

if 0 < tbl < FSIZE:
    print("表绝对偏移 0x%X, 需要 %d 字节, 结束 0x%X (文件 0x%X)" %
          (BASE + tbl, count * 8, BASE + tbl + count * 8, FSIZE))
    ok = BASE + tbl + count * 8 <= FSIZE
    print("范围检查: %s" % ("OK" if ok else "超出!"))

    if ok and count > 0:
        # 看前几条的 ID 是否像打包 ID（高 8 位是合理长度）
        print("\n--- 前 20 条 (id, idx) ---")
        sane = 0
        for i in range(min(count, 2000)):
            pid, idx = struct.unpack_from("<Ii", BUF, BASE + tbl + i * 8)
            ln = (pid >> 24) & 0xFF
            if 2 <= ln <= 120:
                sane += 1
            if i < 20:
                print("  [%5d] id=%08X len=%-3d idx=%06X  idxfield=%-8d" %
                      (i, pid, ln, pid & 0xFFFFFF, idx))
        print("\n前 2000 条中 length 合理的: %d (%.1f%%)" % (sane, 100.0 * sane / min(count, 2000)))
