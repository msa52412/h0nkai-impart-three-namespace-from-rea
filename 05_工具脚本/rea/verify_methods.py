#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证方法名表解密（dec_str.c:1149-1156）。

  uVar7 = ((((uVar10 * 0xB069) ^ 0x3E382F2D) * 0x24147491 ^ 0xF997B4A800) >> 10)
           * 0x3857AACA >> 0xE;                       // 全 64 位
  lVar3 = (DAT_188198e58 - 0x17A3B99) + s_GlobalMetadata;   // 0xFA8318
  lVar5 = uVar10 * 0x20;
  method_name_id = *(uint*)(lVar5 + 0x0C + lVar3) ^ uVar7 ^ 0x1D64B276;
  flag = (*(u8*)(lVar5 + 0x1C + lVar3) - 0x10 ^ uVar7) & 0x10;
"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
OUT = r"D:\Carol-start\_rea\bh3_methods.txt"

BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x20

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
TBL_OFF = (u32va(0x188198E58) - 0x017A3B99) & M32
K_MUL = (-0x394A88E12FFFF3A0) & M64
K_ADD = 0x53DB1FC7E9ECC644
K_STEP = 0x64C7CE0352814CF6

with open(META, "rb") as f:
    BUF = f.read()
FSIZE = len(BUF)
POOL_ABS = BASE + POOL_OFF
TBL_ABS = BASE + TBL_OFF
_U64 = struct.Struct("<Q")

print("池 0x%X, 方法表 0x%X (offset 0x%X), 步长 0x%X" % (POOL_ABS, TBL_ABS, TBL_OFF, STEP))
print("表区可用 %d 字节 -> 最多 %d 条" % (FSIZE - TBL_ABS, (FSIZE - TBL_ABS) // STEP))


def prf(i):
    x = ((i * 0xB069) ^ 0x3E382F2D) & M64
    x = (x * 0x24147491) & M64
    x = x ^ 0xF997B4A800
    x = x >> 10
    x = (x * 0x3857AACA) & M64
    return x >> 0xE


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


print("\n--- 前 20 条 ---")
for i in range(20):
    off = TBL_ABS + i * STEP
    raw_id = struct.unpack_from("<I", BUF, off + 0x0C)[0]
    flag = BUF[off + 0x1C]
    p = prf(i)
    pid = (raw_id ^ p ^ 0x1D64B276) & M32
    f2 = ((flag - 0x10) & 0xFF) ^ (p & 0xFF)
    s = decrypt_str(pid)
    print("  [%5d] raw=%08X prf=%016X id=%08X len=%3d -> %r  flag=%02X/%02X" %
          (i, raw_id, p, pid, (pid >> 24) & 0xFF, s, flag, f2))

# 统计前 N 条的命中率
N = 5000
ok = 0
bad = 0
for i in range(N):
    off = TBL_ABS + i * STEP
    if off + STEP > FSIZE:
        break
    raw_id = struct.unpack_from("<I", BUF, off + 0x0C)[0]
    pid = (raw_id ^ prf(i) ^ 0x1D64B276) & M32
    ln = (pid >> 24) & 0xFF
    if 1 <= ln <= 120:
        s = decrypt_str(pid)
        if s:
            ok += 1
        else:
            bad += 1
print("\n前 %d 条: 解出 %d, length合理但解密失败 %d" % (N, ok, bad))
