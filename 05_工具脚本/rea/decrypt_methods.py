#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析 FUN_1804409f0 的「方法名表」：{字符串ID(明文), 函数指针索引}，步长 8。

伪代码 dec_str.c:1269-1273:
  lVar9 = (DAT_188198e98 + -0x56ca4fe4) + s_GlobalMetadata;
  uVar7 = ((DAT_188198e88 >> 3) ^ 0xd9bea51);       // 条数
  for i: name = FUN_18043ab50(*(u32*)(lVar9 + i*8)); idx = *(i32*)(lVar9+4+i*8);
"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
OUT = r"D:\Carol-start\_rea\bh3_methods.txt"
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


POOL_OFF = u32va(0x188198E50) ^ 0x7483FF7A
K_MUL = (-0x394A88E12FFFF3A0) & M64
K_ADD = 0x53DB1FC7E9ECC644
K_STEP = 0x64C7CE0352814CF6

with open(META, "rb") as f:
    BUF = f.read()
FSIZE = len(BUF)
POOL_ABS = BASE + POOL_OFF
_U64 = struct.Struct("<Q")

V98 = u32va(0x188198E98)
V88 = u32va(0x188198E88)
TBL_OFF = (V98 - 0x56CA4FE4) & M32
COUNT = ((V88 >> 3) ^ 0xD9BEA51) & M32

print("DAT_188198e98 = 0x%08X  ->  表偏移 0x%X (%d)" % (V98, TBL_OFF, TBL_OFF))
print("DAT_188198e88 = 0x%08X  ->  条数 %d (0x%X)" % (V88, COUNT, COUNT))
print("表绝对偏移 0x%X, 需要 %d 字节, 文件 %d" % (BASE + TBL_OFF, COUNT * 8, FSIZE))

TBL_ABS = BASE + TBL_OFF
if TBL_ABS + COUNT * 8 > FSIZE:
    print("!! 超出文件范围，条数可能算错")
    COUNT = min(COUNT, (FSIZE - TBL_ABS) // 8)
    print("   截断到 %d 条" % COUNT)


def decrypt_str(pid):
    length = (pid >> 24) & 0xFF
    index = pid & 0xFFFFFF
    if length == 0:
        return ""
    if length > 0x100:
        return None
    src = POOL_ABS + index
    nb = (length + 7) >> 3
    if src + nb * 8 > FSIZE:
        return None
    key = (index * K_MUL + K_ADD) & M64
    out = bytearray()
    for b in range(nb):
        c = _U64.unpack_from(BUF, src + b * 8)[0]
        out += (c ^ key).to_bytes(8, "little")
        key = (key + K_STEP) & M64
    return out[:length].split(b"\0")[0].decode("utf-8", "replace")


print("\n--- 前 25 条原始记录 ---")
for i in range(25):
    pid, idx = struct.unpack_from("<Ii", BUF, TBL_ABS + i * 8)
    s = decrypt_str(pid)
    print("  [%5d] id=%08X idx=%-6d  %s" % (i, pid, idx, s))

ok = 0
rows = []
for i in range(COUNT):
    pid, idx = struct.unpack_from("<Ii", BUF, TBL_ABS + i * 8)
    s = decrypt_str(pid)
    if s:
        ok += 1
    rows.append((i, pid, idx, s))

print("\n解密成功 %d / %d (%.1f%%)" % (ok, COUNT, 100.0 * ok / COUNT if COUNT else 0))

with open(OUT, "w", encoding="utf-8") as f:
    for i, pid, idx, s in rows:
        f.write("%d\t%d\t%s\n" % (i, idx, s or ""))
print("写出 %s" % OUT)

print("\n--- 抽样 20 条已解出的 ---")
n = 0
for i, pid, idx, s in rows:
    if s and n < 20:
        print("  [%5d] idx=%-6d %s" % (i, idx, s))
        n += 1
