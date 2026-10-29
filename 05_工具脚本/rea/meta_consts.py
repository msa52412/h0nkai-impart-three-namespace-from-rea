#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 UserAssembly.dll 提取 metadata 解密常量（只算常量，不依赖 Z 盘）。"""
import struct, json, os

DLL = r"D:\BH3\7.0\BH3_Data\Native\UserAssembly.dll"
if not os.path.exists(DLL):
    DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"

dll = open(DLL, "rb").read()
e_lfanew = struct.unpack_from("<I", dll, 0x3C)[0]
coff = e_lfanew + 4
nsec = struct.unpack_from("<H", dll, coff + 2)[0]
optsz = struct.unpack_from("<H", dll, coff + 16)[0]
opt = coff + 20
IMAGE_BASE = struct.unpack_from("<Q", dll, opt + 24)[0]
SECS = []
sh = opt + optsz
for i in range(nsec):
    o = sh + i * 40
    vs, va, rs, rp = struct.unpack_from("<IIII", dll, o + 8)
    SECS.append((va, vs, rs, rp))


def va2off(va):
    rva = va - IMAGE_BASE
    for vaddr, vsize, rsize, rptr in SECS:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return None if rsize == 0 else rptr + (rva - vaddr)
    return None


def u32va(va):
    o = va2off(va)
    return None if o is None else struct.unpack_from("<I", dll, o)[0]


POOL_OFF = u32va(0x188198E50) ^ 0x7483FF7A
T5_OFF = u32va(0x188198E1C) ^ 0x72267500
N_TABLES = (u32va(0x188198E4C) ^ 0x6F3F9184) // 0x28

print("DLL =", DLL)
print("IMAGE_BASE = 0x%X" % IMAGE_BASE)
print("POOL_OFF   = 0x%08X" % POOL_OFF)
print("T5_OFF     = 0x%08X" % T5_OFF)
print("N_TABLES   =", N_TABLES)

json.dump({"POOL_OFF": POOL_OFF, "T5_OFF": T5_OFF, "N_TABLES": N_TABLES, "BASE": 0x118},
          open(r"D:\Carol-start\_rea\meta_consts.json", "w"))
print("[+] meta_consts.json")
