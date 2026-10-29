#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
崩坏3 global-metadata.dat 离线解密器（路线 B 完整实现）

原理（全部来自 Ghidra 反编译 + 实测验证）:
  s_GlobalMetadata = buf + 0x118

  1) 字符串池按需解密  FUN_18043ab50(packed_id)
       len   = (id >> 24) & 0xFF
       index = id & 0xFFFFFF
       src   = s_GlobalMetadata + (DAT_188198e50 ^ 0x7483ff7a) + index
       key   = index * 0xC6B5771ED0000C60 + 0x53DB1FC7E9ECC644   (mod 2^64)
       每 8 字节: plain = cipher ^ key;  key += 0x64C7CE0352814CF6

  2) 192 张表描述符  表5 区  offset 0x01C2A198  步长 0x28
       每条记录的字段用 prf(i) 扰动后再异或/加减固定常量

  3) prf(i) = (int32)(( ((i * 0x14C3BD9234D3) >> 9) + 0x48C65E21 ) * 0x22343DDF >> 21)
        —— 必须全 64 位运算，最后才截断成 int32

用法:
    python bh3_meta_decrypt.py
输出:
    bh3_metadata_tables.json   192 张表的结构
    bh3_metadata_strings.txt   解出的全部字符串
"""
import json
import struct
import sys

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
OUT_TABLES = r"D:\Carol-start\_rea\bh3_metadata_tables.json"
OUT_STRINGS = r"D:\Carol-start\_rea\bh3_metadata_strings.txt"

BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF


def i32(x):
    x &= M32
    return x - (1 << 32) if x >= (1 << 31) else x


def u32(x):
    return x & M32


# ============ 1. 从 DLL 读常量 ============
with open(DLL, "rb") as f:
    dll = f.read()

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


POOL_OFF = u32va(0x188198E50) ^ 0x7483FF7A          # 字符串池偏移
T5_OFF = u32va(0x188198E1C) ^ 0x72267500            # 表描述符区偏移
T7_OFF = u32va(0x188198E60) ^ 0x371B8070            # 表7 区
T8_OFF = u32va(0x188198E70) ^ 0x0561C6FD            # 表8 区
T9_OFF = (u32va(0x188198E58) - 0x017A3B99) & M32    # 表9 区
N_TABLES = (u32va(0x188198E4C) ^ 0x6F3F9184) // 0x28  # = 192

K_MUL = (-0x394A88E12FFFF3A0) & M64
K_ADD = 0x53DB1FC7E9ECC644
K_STEP = 0x64C7CE0352814CF6

print("[*] DLL 常量")
print("    字符串池 offset   = 0x%08X" % POOL_OFF)
print("    表描述符 offset   = 0x%08X" % T5_OFF)
print("    表7 offset        = 0x%08X" % T7_OFF)
print("    表8 offset        = 0x%08X" % T8_OFF)
print("    表9 offset        = 0x%08X" % T9_OFF)
print("    表数量            = %d" % N_TABLES)

# ============ 2. 读 metadata ============
with open(META, "rb") as f:
    BUF = f.read()
FSIZE = len(BUF)
print("    metadata 大小     = %d (0x%X)" % (FSIZE, FSIZE))


# ============ 3. 字符串解密 ============
def decrypt_str(packed_id):
    """FUN_18043ab50"""
    length = (packed_id >> 24) & 0xFF
    index = packed_id & 0xFFFFFF
    if length == 0:
        return ""
    if length > 0x100:
        return None
    src = BASE + POOL_OFF + index
    nblocks = (length + 7) >> 3
    if src < 0 or src + nblocks * 8 > FSIZE:
        return None
    key = (index * K_MUL + K_ADD) & M64
    out = bytearray()
    for b in range(nblocks):
        cipher = struct.unpack_from("<Q", BUF, src + b * 8)[0]
        out += struct.pack("<Q", cipher ^ key)
        key = (key + K_STEP) & M64
    return out[:length].split(b"\0")[0].decode("utf-8", "replace")


# ============ 4. PRF ============
K1, C1, K2 = 0x14C3BD9234D3, 0x48C65E21, 0x22343DDF


def prf(i):
    """必须全 64 位，最后截 int32"""
    return i32(((((i * K1) >> 9) + C1) * K2) >> 21)


# ============ 5. 解表描述符 ============
# 伪代码 dec_targets.c:338-406
#   f_k = 32 位运算，iVar5 = prf(i)
def decode_record(i, rec):
    p = prf(i)

    def w(x):
        return u32(x)

    return {
        # piVar15[6]  <- rec[0]
        "f00_rt18": w(((w(rec[0] - 0x36D7455A) - p)) ^ 0x61A2155E),
        # piVar15[4]  <- rec[1]
        "f04_rt10": w((w(rec[1] - p) + 0x1298B083)),
        # piVar15[1]  <- rec[2]
        "f08_rt04": w(((w(rec[2] - 0x3B4B92FD) - p)) ^ 0x5887C8C6),
        # *piVar15    <- rec[3]
        "f0C_rt00": w((w(rec[3] - p) - 0x3640F13B)),
        # piVar15[7]  <- rec[4]
        "f10_rt1C": w(((w(rec[4] - 0x7C293E16) - p)) ^ 0x53C69178),
        # 表名字符串 ID <- rec[5]
        "f14_nameid": w(w(rec[5] - 0x3D7DC690) - p),
        # 表6 索引    <- rec[6]  (-1 表示无)
        "f18_typeidx": i32(w(rec[6] - 0x12813D35) - p),
        # piVar15[8]  <- rec[7]
        "f1C_rt20": w(((w(rec[7] ^ 0x16A0E2A5) - p) + 0x3A0AAEFE)),
        # piVar15[5]  <- rec[8]
        "f20_rt14": w(((w(rec[8] - 0x3D2E6FE3) - p)) ^ 0x1D3B2899),
        # piVar15[0x10] <- rec[9]
        "f24_rt40": w(((w(rec[9] ^ 0x0CA5B561) - p) + 0x27FD9462)),
    }


t5_abs = BASE + T5_OFF
tables = []
for i in range(N_TABLES):
    rec = struct.unpack_from("<10I", BUF, t5_abs + i * 0x28)
    d = decode_record(i, rec)
    name = decrypt_str(d["f14_nameid"])
    d["index"] = i
    d["name"] = name
    d["raw"] = ["%08X" % v for v in rec]
    tables.append(d)

print("\n[*] 前 20 张表")
print("%-4s %-40s %-10s %-10s %-10s %-10s" % ("#", "表名", "f00", "f04", "f08", "f0C"))
for t in tables[:20]:
    print("%-4d %-40s %-10d %-10d %-10d %-10d" %
          (t["index"], (t["name"] or "?")[:40], t["f00_rt18"], t["f04_rt10"], t["f08_rt04"], t["f0C_rt00"]))

named = sum(1 for t in tables if t["name"])
print("\n[*] 成功解出表名: %d/%d" % (named, N_TABLES))

# 统计哪些字段像 offset / count
print("\n[*] 字段量级统计（判断谁是 offset / count / size）")
for k in ["f00_rt18", "f04_rt10", "f08_rt04", "f0C_rt00", "f10_rt1C", "f1C_rt20", "f20_rt14", "f24_rt40"]:
    vals = [t[k] for t in tables]
    inrange = sum(1 for v in vals if v < FSIZE)
    print("    %-10s min=%-12d max=%-12d  <文件大小:%3d/%d  uniq=%d" %
          (k, min(vals), max(vals), inrange, N_TABLES, len(set(vals))))

# ============ 6. 导出 ============
with open(OUT_TABLES, "w", encoding="utf-8") as f:
    json.dump({"pool_offset": POOL_OFF, "n_tables": N_TABLES, "tables": tables},
              f, ensure_ascii=False, indent=1)

# 解出字符串池全部字符串（按 index 扫描）
# 用已解出的表名推断池大小，再按 id 逐个试
strs = []
seen = set()
for t in tables:
    for key in ("f14_nameid",):
        sid = t[key]
        if sid in seen:
            continue
        seen.add(sid)
        s = decrypt_str(sid)
        if s:
            strs.append((sid, s))

with open(OUT_STRINGS, "w", encoding="utf-8") as f:
    for sid, s in sorted(strs):
        f.write("%08X\t%s\n" % (sid, s))

print("\n[+] 写出 %s" % OUT_TABLES)
print("[+] 写出 %s (%d 条)" % (OUT_STRINGS, len(strs)))
