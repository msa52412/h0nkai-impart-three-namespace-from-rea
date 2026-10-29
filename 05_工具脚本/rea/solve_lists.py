# -*- coding: utf-8 -*-
"""解 metadataUsageLists（E74 表）：8B {count@+0, start@+4}，keyA(rangeIdx) 解密
   同时核对 E74/E10 是否真的同段；32/64 位 key 双版本测试"""
import struct
import sys

sys.path.insert(0, r"D:\Carol-start\_rea")
from probe_thunk import PE

pe = PE(r"D:\Carol-start\_rea\UserAssembly_slim.dll")
BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
M32 = 0xFFFFFFFF
M64 = (1 << 64) - 1

raw_e74 = struct.unpack_from("<I", pe.d, pe.va2off(0x188198E74))[0]
raw_e10 = struct.unpack_from("<I", pe.d, pe.va2off(0x188198E10))[0]
seg_e74 = raw_e74 ^ 0x3D61FF56
seg_e10 = (raw_e10 + 0xEB3AA0A1) & M32
print("E74 raw=0x%08X ^0x3D61FF56 -> 0x%08X" % (raw_e74, seg_e74))
print("E10 raw=0x%08X +0xEB3AA0A1 -> 0x%08X" % (raw_e10, seg_e10))


def keyA64(i):
    r = (i * 0x34C4) & M64
    r ^= 0x2B6AE776
    r = (r * 0x413A9E4E + 0x224C5174) & M64
    return (r ^ 0x28B14852) & M32


def keyA32(i):
    r = (i * 0x34C4) & M32
    r ^= 0x2B6AE776
    r = (r * 0x413A9E4E + 0x224C5174) & M32
    return r ^ 0x28B14852


TBL = 0x118 + seg_e74
print("\nusageLists 表基 0x%X，双版本测试前 3000 行（count<=64 且 start+count<=263700）:" % TBL)
for name, kf in (("32位", keyA32), ("64位", keyA64)):
    ok = 0
    first_bad = None
    for i in range(3000):
        r0 = struct.unpack_from("<I", BUF, TBL + i * 8)[0]
        r1 = struct.unpack_from("<I", BUF, TBL + i * 8 + 4)[0]
        k = kf(i)
        cnt = ((r0 + 0xB91CB5B5) & M32) ^ k
        st = ((r1 + 0xC938EAC6) & M32) ^ k
        if cnt <= 64 and st + cnt <= 263700:
            ok += 1
        elif first_bad is None:
            first_bad = (i, cnt, st)
    print("  %s key: 合法 %d/3000, 首坏 %s" % (name, ok, first_bad))

# 顺带在 DLL 里找 DefaultValue 相关符号串
import re
hits = set()
for m in re.finditer(rb"[ -~]{6,}", pe.d):
    s = m.group()
    if b"DefaultValue" in s or b"FieldDefault" in s:
        hits.add(s[:80].decode("latin-1"))
print("\nDLL 内含 DefaultValue 的字符串 %d 条:" % len(hits))
for h in sorted(hits)[:20]:
    print("  ", h)
