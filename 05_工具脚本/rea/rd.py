#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按 VA 直接读 dll 里的 dword/qword/bytes（只读）。"""
import struct
import sys

PATH = r"Z:\AI\7.0\BH3_Data\Native\UserAssembly.dll"
IB = 0x180000000
d = open(PATH, "rb").read()

e = struct.unpack_from("<I", d, 0x3C)[0]
coff = e + 4
nsec = struct.unpack_from("<H", d, coff + 2)[0]
optsz = struct.unpack_from("<H", d, coff + 16)[0]
SECS = []
for i in range(nsec):
    o = coff + 20 + optsz + i * 40
    nm = d[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((nm, va, vs, rs, rp))


def va2off(va):
    rva = va - IB
    for nm, sva, vs, rs, rp in SECS:
        if sva <= rva < sva + max(vs, rs):
            if rp == 0:
                return None
            return rp + (rva - sva)
    return None


def main():
    for a in sys.argv[1:]:
        va = int(a, 16)
        off = va2off(va)
        if off is None:
            print("0x%X  无文件映射" % va)
            continue
        b = d[off:off + 32]
        u32 = struct.unpack_from("<I", b, 0)[0]
        s32 = struct.unpack_from("<i", b, 0)[0]
        u64 = struct.unpack_from("<Q", b, 0)[0]
        print("0x%X  off=0x%X  u32=0x%08X (%d)  i32=%d  u64=0x%016X  hex=%s"
              % (va, off, u32, u32, s32, u64, b[:16].hex()))


if __name__ == "__main__":
    main()
