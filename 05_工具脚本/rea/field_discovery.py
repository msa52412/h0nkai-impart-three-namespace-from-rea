#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字段自动发现：对指定表区域的每个 int32 字段位置批量尝试字符串解密，
命中率接近 100% 的字段即为"打包字符串 ID"字段。

这样不需要逐段反编译猜结构，用数据本身说话。
"""
import struct
import sys

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


POOL_OFF = u32va(0x188198E50) ^ 0x7483FF7A
K_MUL = (-0x394A88E12FFFF3A0) & M64
K_ADD = 0x53DB1FC7E9ECC644
K_STEP = 0x64C7CE0352814CF6

with open(META, "rb") as f:
    BUF = f.read()
FSIZE = len(BUF)
POOL_ABS = BASE + POOL_OFF

# 预取 2 块的密文读取器


def try_str(pid, min_len=2, max_len=120):
    length = (pid >> 24) & 0xFF
    if length < min_len or length > max_len:
        return None
    index = pid & 0xFFFFFF
    src = POOL_ABS + index
    nb = (length + 7) >> 3
    if src + nb * 8 > FSIZE:
        return None
    key = (index * K_MUL + K_ADD) & M64
    out = bytearray()
    for b in range(nb):
        c = struct.unpack_from("<Q", BUF, src + b * 8)[0]
        out += (c ^ key).to_bytes(8, "little")
        key = (key + K_STEP) & M64
    cand = out[:length]
    # 快速判据：可打印 ASCII 占比
    ok = 0
    for ch in cand:
        if 0x20 <= ch <= 0x7E or ch >= 0x80:
            ok += 1
    if ok < length:
        return None
    try:
        s = cand.decode("utf-8")
    except UnicodeDecodeError:
        return None
    for ch in s:
        o = ord(ch)
        if o < 0x20 or o == 0x7F:
            return None
    return s


def scan_region(name, off, step, count, max_count=None):
    """对区域每个字段位置统计命中率"""
    abs_off = BASE + off
    nf = step // 4
    if max_count:
        count = min(count, max_count)
    if abs_off + step * count > FSIZE:
        count = (FSIZE - abs_off) // step
    if count <= 0:
        print("  [%s] 区域越界" % name)
        return None
    print("\n" + "=" * 90)
    print("区域 %s  offset=0x%X  step=0x%X  count=%d  字段数=%d" % (name, off, step, count, nf))
    print("=" * 90)
    best = []
    for k in range(nf):
        hit = 0
        total_len = 0
        samples = []
        for i in range(count):
            v = struct.unpack_from("<I", BUF, abs_off + i * step + k * 4)[0]
            s = try_str(v)
            if s:
                hit += 1
                total_len += len(s)
                if len(samples) < 3:
                    samples.append(s)
        rate = 100.0 * hit / count
        if hit > 0:
            print("  +0x%02X: %4d/%d (%5.1f%%)  平均长 %.1f  %s" %
                  (k * 4, hit, count, rate, total_len / hit if hit else 0,
                   " | ".join(x[:22] for x in samples)))
        if rate >= 40:
            best.append((k * 4, rate, samples))
    return best


results = {}
# 0xFA8318 步长 0x5C —— 类型表（dec_targets.c:499-514 的 lVar6）
results["类型表(0xFA8318,0x5C)"] = scan_region("类型表", 0x00FA8318, 0x5C, 30000)
# 0x0512A0 —— 未知区
results["未知区(0x0512A0,0x5C)"] = scan_region("未知区", 0x000512A0, 0x5C, 30000)
# 0x0242D2E8 表7
results["表7(0x242D2E8,0x10)"] = scan_region("表7", 0x0242D2E8, 0x10, 192)

print("\n\n" + "#" * 90)
print("汇总：命中率 >= 40% 的字段")
print("#" * 90)
for name, b in results.items():
    if b:
        print("%s:" % name)
        for off, rate, samples in b:
            print("   +0x%02X  %.1f%%  %s" % (off, rate, samples[:2]))
    else:
        print("%s: 无" % name)
