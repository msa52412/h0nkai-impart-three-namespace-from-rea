#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_typerec.py — 扫类型记录 0x5C 里的每个 dword，找 instance_size / static_fields_size 线索

校验目标（已知地面真值）：
  Vector3 实例 12 字节（get_magnitude 访问 +0/+4/+8）
  Vector2 实例 8 字节
  String  m_stringLength@+0x10, m_firstChar@+0x14
"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x5C
NT = 57487
BASE = 0x118

d = open(DLL, "rb").read()
e = struct.unpack_from("<I", d, 0x3C)[0]
coff = e + 4
nsec = struct.unpack_from("<H", d, coff + 2)[0]
optsz = struct.unpack_from("<H", d, coff + 16)[0]
opt = coff + 20
IB = struct.unpack_from("<Q", d, opt + 24)[0]
SECS = []
sh = opt + optsz
for i in range(nsec):
    o = sh + i * 40
    nm = d[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((nm, va, vs, rs, rp))


def va2off(va):
    rva = va - IB
    for nm, vaddr, vsize, rsize, rptr in SECS:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return None if rsize == 0 else rptr + (rva - vaddr)
    return None


def u32va(va):
    o = va2off(va)
    return None if o is None else struct.unpack_from("<I", d, o)[0]


BUF = open(META, "rb").read()
FSIZE = len(BUF)
TYPE_OFF = (u32va(0x188198E08) ^ 0x2B849DB3) & M32
POOL_OFF = u32va(0x188198E50) ^ 0x7483FF7A
T0 = BASE + TYPE_OFF
P_ABS = BASE + POOL_OFF
K_MUL = (-0x394A88E12FFFF3A0) & M64
K_ADD = 0x53DB1FC7E9ECC644
K_STEP = 0x64C7CE0352814CF6
_u64 = struct.Struct("<Q")

SALT = []
for i in range(NT):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    SALT.append(((x * 0x1125F1B6) & M64) & M32)


def dec(pid):
    L = (pid >> 24) & 0xFF
    if L == 0 or L > 0x40:
        return None
    ix = pid & 0xFFFFFF
    src = P_ABS + ix
    nb = (L + 7) >> 3
    if src + nb * 8 > FSIZE:
        return None
    key = (ix * K_MUL + K_ADD) & M64
    out = bytearray()
    for b in range(nb):
        out += (_u64.unpack_from(BUF, src + b * 8)[0] ^ key).to_bytes(8, "little")
        key = (key + K_STEP) & M64
    try:
        t = out[:L].decode("utf-8")
    except UnicodeDecodeError:
        return None
    for ch in t:
        if ord(ch) < 0x20 or ord(ch) == 0x7F:
            return None
    return t


def full(i):
    off = T0 + i * STEP
    r = struct.unpack_from("<23I", BUF, off)
    s = SALT[i]
    nm = dec((((r[13] ^ 0x3399EFB) - s) & M32))
    ns = dec(((((r[12] - s) & M32) - 0x4B6ACCC7) & M32)) or ""
    return (ns + "." if ns else "") + (nm or "?"), r, s


# 已知类型
TARGETS = {}
for i in range(NT):
    n, r, s = full(i)
    if n in ("UnityEngine.Vector3", "UnityEngine.Vector2", "System.String",
             "System.Object", "UnityEngine.Quaternion", "UnityEngine.Color",
             "UnityEngine.Matrix4x4", "UnityEngine.Rect", "System.DateTime",
             "UnityEngine.Vector4", "UnityEngine.Bounds"):
        TARGETS[n] = i

print("[已知类型]")
for n, i in sorted(TARGETS.items(), key=lambda kv: kv[1]):
    print("   %-26s t=%d" % (n, i))

print("\n[逐列 dword 对照]  (列号 = dword 下标)")
names = sorted(TARGETS)
hdr = "col  " + "  ".join("%-10s" % n.split(".")[-1][:10] for n in names)
print(hdr)
recs = {n: full(TARGETS[n])[1] for n in names}
for c in range(23):
    vals = [recs[n][c] for n in names]
    # 只打印至少有一个值是小整数（< 0x10000）的列
    if not any(v < 0x10000 for v in vals):
        continue
    print("r[%2d] " % c + "  ".join("%-10d" % v if v < 0x100000 else "%-10s" % ("%08X" % v) for v in vals))

print("\n[重点校验] Vector3 应为 12 / Vector2 应为 8")
for n in ("UnityEngine.Vector3", "UnityEngine.Vector2", "System.String"):
    r = recs[n]
    print("  %-22s 命中 12 的列: %s" % (n, [c for c in range(23) if r[c] == 12]))
    print("  %-22s 命中  8 的列: %s" % ("", [c for c in range(23) if r[c] == 8]))
