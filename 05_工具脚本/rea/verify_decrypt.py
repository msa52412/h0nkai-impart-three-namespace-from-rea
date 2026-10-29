#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证 FUN_18043ab50 = "按需解密 + 缓存" 原语。

伪代码（dec_core.c:38-104）:
  uVar9 = (param_1 >> 0x18) & 0xff;                       // 高 8 位 = 长度
  uVar6 = (index) * -0x394a88e12ffff3a0 + 0x53db1fc7e9ecc644;   // 密钥种子
  puVar2 = (DAT_188198e50 ^ 0x7483ff7a) + index + s_GlobalMetadata;
  uVar4 = len + 7;  uVar8 = uVar4 >> 3;                   // 8 字节块数
  do { *dst++ = *src++ ^ key; key += 0x64c7ce0352814cf6; } while (--uVar8);

调用点（dec_targets.c:341）:
  id = (piVar17[5] - 0x3d7dc690) - prf(i)
"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF


def i32(x):
    x &= M32
    return x - (1 << 32) if x >= (1 << 31) else x


def u32(x):
    return x & M32


# ---------- PE: 读全局常量 ----------
with open(DLL, "rb") as f:
    dll = f.read()

e = struct.unpack_from("<I", dll, 0x3C)[0]
coff = e + 4
nsec = struct.unpack_from("<H", dll, coff + 2)[0]
optsz = struct.unpack_from("<H", dll, coff + 16)[0]
opt = coff + 20
IB = struct.unpack_from("<Q", dll, opt + 24)[0]
SEC = []
sh = opt + optsz
for i in range(nsec):
    o = sh + i * 40
    vs, va, rs, rp = struct.unpack_from("<IIII", dll, o + 8)
    SEC.append((va, vs, rs, rp))


def va2off(va):
    rva = va - IB
    for vaddr, vsize, rsize, rptr in SEC:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            if rsize == 0:
                return None
            return rptr + (rva - vaddr)
    return None


def u32va(va):
    o = va2off(va)
    return None if o is None else struct.unpack_from("<I", dll, o)[0]


POOL_MASK = 0x7483FF7A
V_POOL = u32va(0x188198E50)
POOL_OFF = V_POOL ^ POOL_MASK
print("DAT_188198e50 = 0x%08X" % V_POOL)
print("pool offset   = 0x%08X ^ 0x%08X = 0x%08X (%d)" % (V_POOL, POOL_MASK, POOL_OFF, POOL_OFF))
print("pool 文件偏移 = 0x118 + 0x%X = 0x%X" % (POOL_OFF, BASE + POOL_OFF))
print()

# ---------- 读 metadata ----------
with open(META, "rb") as f:
    f.seek(0, 2)
    FSIZE = f.tell()
    f.seek(BASE + 0x01C2A198)
    T5 = f.read(0x28 * 192)
    f.seek(0)
    META_ALL = f.read()   # 56 MB，够用

RECS = [struct.unpack_from("<10I", T5, i * 0x28) for i in range(192)]

K_MUL = (-0x394A88E12FFFF3A0) & M64
K_ADD = 0x53DB1FC7E9ECC644
K_STEP = 0x64C7CE0352814CF6

print("K_MUL = 0x%016X" % K_MUL)
print()


def decrypt_str(idx, length):
    """按 FUN_18043ab50 的算法解密。"""
    if length <= 0 or length > 0x100:
        return None
    src = BASE + POOL_OFF + idx
    nblocks = (length + 7) >> 3
    need = nblocks * 8
    if src < 0 or src + need > FSIZE:
        return None
    key = (idx * K_MUL + K_ADD) & M64
    out = bytearray()
    for b in range(nblocks):
        cipher = struct.unpack_from("<Q", META_ALL, src + b * 8)[0]
        plain = cipher ^ key
        out += struct.pack("<Q", plain)
        key = (key + K_STEP) & M64
    return bytes(out[:length])


def printable_ratio(bs):
    if not bs:
        return 0.0
    ok = sum(1 for c in bs if 0x20 <= c <= 0x7E or c in (9, 10, 13))
    return ok / len(bs)


# ---------- PRF 语义变体 ----------
K1 = 0x14C3BD9234D3
C1 = 0x48C65E21
K2 = 0x22343DDF


def prf_64(i):
    return i32(((((i * K1) >> 9) + C1) * K2) >> 21)


def prf_mul32(i):
    x = ((i * K1) >> 9) + C1
    return i32(((u32(x) * K2) & M32) >> 21)


def prf_add32(i):
    x = u32(((i * K1) >> 9)) + C1
    return i32(((u32(x) * K2) & M32) >> 21)


def prf_all32(i):
    x = u32(((u32(i) * u32(K1)) & M32) >> 9) + C1
    return i32(((u32(x) * K2) & M32) >> 21)


def prf_none(i):
    return 0


PRFS = {
    "全64位": prf_64,
    "乘后截32": prf_mul32,
    "加后截32": prf_add32,
    "全32位": prf_all32,
    "无PRF": prf_none,
}

print("=" * 96)
print("表5 piVar17[5] -> id -> 解密字符串，统计可打印率（正确的话应接近 100%%）")
print("=" * 96)
print("%-12s %-10s %-12s %-12s %s" % ("PRF", "有效解出", "平均可打印率", "len合理数", "示例"))

best = None
for name, fn in PRFS.items():
    good = 0
    ratios = []
    lenok = 0
    samples = []
    for i in range(192):
        idv = i32(i32(RECS[i][5] - 0x3D7DC690) - fn(i))
        length = (idv >> 24) & 0xFF
        idx = idv & 0xFFFFFF
        if 1 <= length <= 80:
            lenok += 1
        s = decrypt_str(idx, length)
        if s is None:
            continue
        good += 1
        r = printable_ratio(s)
        ratios.append(r)
        if r > 0.9 and len(samples) < 3:
            samples.append(s)
    avg = sum(ratios) / len(ratios) if ratios else 0.0
    ex = samples[0][:40] if samples else b""
    print("%-12s %-10s %-12s %-12s %r" % (name, "%d/192" % good, "%.1f%%" % (avg * 100), lenok, ex))
    if best is None or avg > best[1]:
        best = (name, avg)

print("\n最佳 PRF: %s (平均可打印率 %.1f%%)" % (best[0], best[1] * 100))

# 用最佳 PRF 打印前 12 条解密结果
fn = PRFS[best[0]]
print("\n--- 用 %s 解出的前 12 条 ---" % best[0])
for i in range(12):
    idv = i32(i32(RECS[i][5] - 0x3D7DC690) - fn(i))
    length = (idv >> 24) & 0xFF
    idx = idv & 0xFFFFFF
    s = decrypt_str(idx, length)
    print("  [%3d] raw=%08X id=%08X len=%3d idx=%06X -> %r" %
          (i, RECS[i][5], idv & M32, length, idx, s))
