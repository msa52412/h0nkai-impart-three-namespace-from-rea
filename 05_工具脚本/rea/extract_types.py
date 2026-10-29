#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
类型表全量提取 + 字段语义自动识别

记录布局：0x5C = 92 字节 = 23 个 dword，与标准 Il2CppTypeDefinition 尺寸一致
  已知（来自 asm_42b910.txt）:
    +0x30  namespace  -> dec((raw - salt - 0x4B6ACCC7))
    +0x34  name       -> dec((raw ^ 0x3399EFB - salt))
  其余字段变换常量未知，用分布统计推断。
"""
import json
import struct
import sys
from collections import Counter

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
OUT_TXT = r"D:\Carol-start\_rea\bh3_types_full.txt"
OUT_JSON = r"D:\Carol-start\_rea\bh3_types.json"

BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x5C

# ---------- PE ----------
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
            return None if rsize == 0 else struct.unpack_from("<I", dll, rptr + (rva - vaddr))[0]
    return None


TYPE_OFF = (u32va(0x188198E08) ^ 0x2B849DB3) & M32
N_TYPE = (u32va(0x1881A3630) ^ 0x421DD17C) & M32
POOL_OFF = u32va(0x188198E50) ^ 0x7483FF7A
K_MUL = (-0x394A88E12FFFF3A0) & M64
K_ADD = 0x53DB1FC7E9ECC644
K_STEP = 0x64C7CE0352814CF6

with open(META, "rb") as f:
    BUF = f.read()
FSIZE = len(BUF)
T_ABS = BASE + TYPE_OFF
P_ABS = BASE + POOL_OFF
_U64 = struct.Struct("<Q")

print("类型表 0x%X @ 0x%X  条数 %d  占用 0x%X  文件 0x%X"
      % (TYPE_OFF, T_ABS, N_TYPE, N_TYPE * STEP, FSIZE))
assert T_ABS + N_TYPE * STEP <= FSIZE, "类型表越界"

# ---------- salt 预计算 ----------
SALT = []
for i in range(N_TYPE):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    SALT.append(((x * 0x1125F1B6) & M64) & M32)

_sc = {}


def dec(pid):
    s = _sc.get(pid, 0)
    if s != 0:
        return s if s != -1 else None
    length = (pid >> 24) & 0xFF
    if length == 0:
        _sc[pid] = -1
        return None
    if length > 0x80:
        _sc[pid] = -1
        return None
    index = pid & 0xFFFFFF
    src = P_ABS + index
    nb = (length + 7) >> 3
    if src + nb * 8 > FSIZE:
        _sc[pid] = -1
        return None
    key = (index * K_MUL + K_ADD) & M64
    out = bytearray()
    for b in range(nb):
        out += (_U64.unpack_from(BUF, src + b * 8)[0] ^ key).to_bytes(8, "little")
        key = (key + K_STEP) & M64
    try:
        t = out[:length].decode("utf-8")
    except UnicodeDecodeError:
        _sc[pid] = -1
        return None
    for ch in t:
        if ord(ch) < 0x20 or ord(ch) == 0x7F:
            _sc[pid] = -1
            return None
    _sc[pid] = t
    return t


# ---------- 读全部记录 ----------
print("[*] 读取 %d 条记录..." % N_TYPE)
REC = []
for i in range(N_TYPE):
    off = T_ABS + i * STEP
    REC.append(struct.unpack_from("<23I", BUF, off))

# ---------- 解 name / namespace ----------
print("[*] 解 name / namespace ...")
types = []
bad = 0
for i in range(N_TYPE):
    r = REC[i]
    s = SALT[i]
    nm = dec((((r[13] ^ 0x3399EFB) - s) & M32))
    ns = dec(((((r[12] - s) & M32) - 0x4B6ACCC7) & M32))
    if nm is None:
        bad += 1
        continue
    types.append((i, nm, ns or ""))
print("    成功 %d / 失败 %d (%.2f%%)" % (len(types), bad, 100.0 * len(types) / N_TYPE))
print("    唯一类型名 %d" % len(set(t[1] for t in types)))
print("    命名空间数 %d" % len(set(t[2] for t in types)))

# ---------- 字段分布统计 ----------
print("\n" + "=" * 78)
print("[*] 23 个 dword 位置的分布特征（用于识别语义）")
print("%-4s %-12s %-12s %-10s %-10s %-8s %s"
      % ("pos", "min(-salt)", "max(-salt)", "uniq", "<10万", "小值%", "样本"))
for p in range(23):
    vals = [((REC[i][p] - SALT[i]) & M32) for i in range(0, N_TYPE, 7)]
    n = len(vals)
    small = sum(1 for v in vals if v < 100000)
    tiny = sum(1 for v in vals if v < 10000)
    print("%-4d %-12d %-12d %-10d %-10d %-8.1f %s"
          % (p, min(vals), max(vals), len(set(vals)), small,
             100.0 * tiny / n, " ".join("%08X" % v for v in vals[:3])))

# ---------- 校验：sum(method_count) 是否等于 408461 ----------
print("\n[*] 用 sum(count)==408461 反查 method_count 字段")
target = 408461
for p in range(23):
    vals = [((REC[i][p] - SALT[i]) & M32) for i in range(N_TYPE)]
    base = min(vals)
    tot = sum(v - base for v in vals if v - base < 100000)
    if abs(tot - target) < target * 0.02:
        print("    pos=%d  base=0x%X  总和=%d  (差 %d)" % (p, base, tot, tot - target))

with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump({"type_off": TYPE_OFF, "count": N_TYPE,
               "types": [[i, n, s] for i, n, s in types]}, f, ensure_ascii=False)
with open(OUT_TXT, "w", encoding="utf-8") as f:
    for i, n, s in types:
        f.write("%d\t%s\t%s\n" % (i, s, n))
print("\n[+] %s" % OUT_TXT)
print("[+] %s" % OUT_JSON)

c = Counter(n for _, n, _ in types)
print("\n--- 高频类型名 25 ---")
for k, v in c.most_common(25):
    print("  %-45s %5d" % (k, v))
cs = Counter(s for _, _, s in types if s)
print("\n--- 命名空间 Top 25 ---")
for k, v in cs.most_common(25):
    print("  %-45s %5d" % (k, v))
