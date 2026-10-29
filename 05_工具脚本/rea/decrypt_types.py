#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解密表8（类型信息）里的两个字符串字段。

伪代码 dec_targets.c:457-489:
  uVar21 = ((i * 0x56184A41 + 0x57A94B1F) ^ 0x37F164B8) * 0x10FB44E5 ^ 0x7B1DE297;  // 表7 PRF
  uVar23 = ( i * 0x447FCE41 ^ 0x120DD35F) * 0x3E8906DA;                            // 表8 PRF
  puVar16 = 表8基址 + i*0x2C
  lVar8  = FUN_18043ab50(puVar16[1] + 0x84B0104A ^ uVar23);
  uVar19 = FUN_18043ab50(puVar16[5] + 0xF54D97A6 ^ uVar23);
  *(u64*)(piVar15+0x13) = *(u64*)(puVar16+9);     // [9],[10] 明文直拷
"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
OUT = r"D:\Carol-start\_rea\bh3_types.txt"

BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF


def i32(x):
    x &= M32
    return x - (1 << 32) if x >= (1 << 31) else x


def u32(x):
    return x & M32


# ---- 常量 ----
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
T5_OFF = u32va(0x188198E1C) ^ 0x72267500
T7_OFF = u32va(0x188198E60) ^ 0x371B8070
T8_OFF = u32va(0x188198E70) ^ 0x0561C6FD
N = (u32va(0x188198E4C) ^ 0x6F3F9184) // 0x28

K_MUL = (-0x394A88E12FFFF3A0) & M64
K_ADD = 0x53DB1FC7E9ECC644
K_STEP = 0x64C7CE0352814CF6

with open(META, "rb") as f:
    BUF = f.read()
FSIZE = len(BUF)


def decrypt_str(pid):
    length = (pid >> 24) & 0xFF
    index = pid & 0xFFFFFF
    if length == 0:
        return ""
    if length > 0x100:
        return None
    src = BASE + POOL_OFF + index
    nb = (length + 7) >> 3
    if src + nb * 8 > FSIZE:
        return None
    key = (index * K_MUL + K_ADD) & M64
    out = bytearray()
    for b in range(nb):
        c = struct.unpack_from("<Q", BUF, src + b * 8)[0]
        out += struct.pack("<Q", c ^ key)
        key = (key + K_STEP) & M64
    return out[:length].split(b"\0")[0].decode("utf-8", "replace")


# ---- PRF ----
def prf7(i):
    return u32(((u32(u32(i * 0x56184A41) + 0x57A94B1F) ^ 0x37F164B8) * 0x10FB44E5) ^ 0x7B1DE297)


def prf8(i):
    return u32(u32(u32(i * 0x447FCE41) ^ 0x120DD35F) * 0x3E8906DA)


t8_abs = BASE + T8_OFF
t7_abs = BASE + T7_OFF
t5_abs = BASE + T5_OFF

rows = []
for i in range(N):
    r8 = struct.unpack_from("<11I", BUF, t8_abs + i * 0x2C)
    p8 = prf8(i)
    id1 = u32(u32(r8[1] + 0x84B0104A) ^ p8)
    id2 = u32(u32(r8[5] + 0xF54D97A6) ^ p8)
    s1 = decrypt_str(id1)
    s2 = decrypt_str(id2)

    r7 = struct.unpack_from("<4I", BUF, t7_abs + i * 0x10)
    p7 = prf7(i)
    asm_idx = i32(u32(r7[2] + 0xFC36A893) - p7)   # 指向表5（程序集）

    rows.append({
        "i": i,
        "name1": s1, "id1": id1,
        "name2": s2, "id2": id2,
        "asm": asm_idx,
        "t8_9": r8[9], "t8_10": r8[10],   # 明文直拷
        "raw8": ["%08X" % v for v in r8],
        "raw7": ["%08X" % v for v in r7],
    })

ok1 = sum(1 for r in rows if r["name1"])
ok2 = sum(1 for r in rows if r["name2"])
print("表8 字符串1 解出: %d/%d" % (ok1, N))
print("表8 字符串2 解出: %d/%d" % (ok2, N))
print()

print("%-4s %-42s %-34s %-6s %s" % ("#", "字段[1] 解出", "字段[5] 解出", "程序集", "明文[9][10]"))
for r in rows[:30]:
    print("%-4d %-42s %-34s %-6s %08X %08X" %
          (r["i"], (r["name1"] or "?")[:42], (r["name2"] or "?")[:34],
           r["asm"], r["t8_9"], r["t8_10"]))

# 明文 [9][10] 的取值分布
from collections import Counter
c9 = Counter(r["t8_9"] for r in rows)
c10 = Counter(r["t8_10"] for r in rows)
print("\n明文 [9] 取值分布:", dict(c9))
print("明文 [10] 取值分布:", dict(c10))

# 程序集索引分布
print("\n程序集索引 (表7[2]) 前 20:", [r["asm"] for r in rows[:20]])

with open(OUT, "w", encoding="utf-8") as f:
    f.write("# 表8 类型信息（i\tdll名\t命名空间/类型名\t程序集索引）\n")
    for r in rows:
        f.write("%d\t%s\t%s\t%d\n" % (r["i"], r["name1"] or "", r["name2"] or "", r["asm"]))
print("\n写出 %s" % OUT)
