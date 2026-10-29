#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
类型表完整提取 + 类型→方法关联

已确认：
  +0x30  namespace          dec((raw - salt - 0x4B6ACCC7))
  +0x34  name               dec((raw ^ 0x3399EFB - salt))
  +0x14  methodStart        (raw - 0x2822B501 - salt)，0 = 无方法
  +0x20  nestedTypesStart   (raw ^ 0x21FE571D - salt)，-1 = 无
  +0x46  nested_type_count  u16 (raw ^ 0x7883) - (salt & 0xFFFF)
  methodCount 由 methodStart 的非空严格递增序列差分得到

产物：
  bh3_types_full.txt    索引 / 命名空间 / 类型名 / methodStart / methodCount
  bh3_types_methods.txt 类型全名 + 其方法名
  bh3_types.json
"""
import json
import struct
from collections import Counter, defaultdict

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
METH = r"D:\Carol-start\_rea\bh3_methods.txt"
OUT_TXT = r"D:\Carol-start\_rea\bh3_types_full.txt"
OUT_M = r"D:\Carol-start\_rea\bh3_types_methods.txt"
OUT_JSON = r"D:\Carol-start\_rea\bh3_types.json"

BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x5C
NT = 57487
N_METHOD = 408461

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
POOL_OFF = u32va(0x188198E50) ^ 0x7483FF7A
K_MUL = (-0x394A88E12FFFF3A0) & M64
K_ADD = 0x53DB1FC7E9ECC644
K_STEP = 0x64C7CE0352814CF6

with open(META, "rb") as f:
    BUF = f.read()
FSIZE = len(BUF)
T0 = BASE + TYPE_OFF
P_ABS = BASE + POOL_OFF
_U64 = struct.Struct("<Q")

SALT = []
for i in range(NT):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    SALT.append(((x * 0x1125F1B6) & M64) & M32)

_sc = {}


def dec(pid):
    if pid in _sc:
        return _sc[pid]
    length = (pid >> 24) & 0xFF
    if length == 0 or length > 0x80:
        _sc[pid] = None
        return None
    index = pid & 0xFFFFFF
    src = P_ABS + index
    nb = (length + 7) >> 3
    if src + nb * 8 > FSIZE:
        _sc[pid] = None
        return None
    key = (index * K_MUL + K_ADD) & M64
    out = bytearray()
    for b in range(nb):
        out += (_U64.unpack_from(BUF, src + b * 8)[0] ^ key).to_bytes(8, "little")
        key = (key + K_STEP) & M64
    try:
        t = out[:length].decode("utf-8")
    except UnicodeDecodeError:
        _sc[pid] = None
        return None
    for ch in t:
        if ord(ch) < 0x20 or ord(ch) == 0x7F:
            _sc[pid] = None
            return None
    _sc[pid] = t
    return t


print("[*] 解 %d 条类型记录 ..." % NT)
recs = []
for i in range(NT):
    off = T0 + i * STEP
    d = struct.unpack_from("<23I", BUF, off)
    s = SALT[i]
    nm = dec((((d[13] ^ 0x3399EFB) - s) & M32))
    ns = dec(((((d[12] - s) & M32) - 0x4B6ACCC7) & M32)) or ""
    ms = ((d[5] - 0x2822B501) - s) & M32
    nest = ((d[8] ^ 0x21FE571D) - s) & M32
    lo16 = struct.unpack_from("<H", BUF, off + 0x46)[0]
    ncnt = ((lo16 ^ 0x7883) - (s & 0xFFFF)) & 0xFFFF
    recs.append({
        "i": i, "name": nm, "ns": ns,
        "methodStart": ms if ms != M32 else -1,
        "nestedStart": nest if nest != M32 else -1,
        "nestedCount": ncnt,
    })
ok = sum(1 for r in recs if r["name"])
print("    成功 %d / %d" % (ok, NT))

# methodStart 非空序列严格递增 -> 差分求 count
nz = [r for r in recs if r["methodStart"] > 0]
print("[*] 有方法的类型 %d 条, start ∈ [%d, %d]"
      % (len(nz), nz[0]["methodStart"], nz[-1]["methodStart"]))
assert all(nz[k + 1]["methodStart"] > nz[k]["methodStart"] for k in range(len(nz) - 1)), "非严格递增"

for k, r in enumerate(nz):
    if k + 1 < len(nz):
        r["methodCount"] = nz[k + 1]["methodStart"] - r["methodStart"]
    else:
        r["methodCount"] = N_METHOD - r["methodStart"]
for r in recs:
    r.setdefault("methodCount", 0)
print("    sum(methodCount) = %d  (方法总数 %d)" % (sum(r["methodCount"] for r in recs), N_METHOD))

# 读方法名
print("[*] 读方法名表 ...")
MNAME = {}
with open(METH, encoding="utf-8") as f:
    for line in f:
        p = line.rstrip("\n").split("\t", 3)
        if len(p) == 4:
            MNAME[int(p[0])] = p[3]
print("    %d 条" % len(MNAME))

# 输出
with open(OUT_TXT, "w", encoding="utf-8") as f:
    f.write("index\tnamespace\ttype\tmethodStart\tmethodCount\n")
    for r in recs:
        f.write("%d\t%s\t%s\t%d\t%d\n"
                % (r["i"], r["ns"], r["name"] or "", r["methodStart"], r["methodCount"]))

print("[*] 写类型→方法 ...")
miss = 0
with open(OUT_M, "w", encoding="utf-8") as f:
    for r in recs:
        if r["methodCount"] <= 0:
            continue
        full = (r["ns"] + "." if r["ns"] else "") + (r["name"] or "?")
        f.write("\n=== %s  (start=%d, count=%d) ===\n" % (full, r["methodStart"], r["methodCount"]))
        for k in range(r["methodStart"], min(r["methodStart"] + r["methodCount"], N_METHOD)):
            n = MNAME.get(k)
            if n is None:
                miss += 1
                n = "<missing:%d>" % k
            f.write("  %s\n" % n)
print("    缺失方法名 %d" % miss)

with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump({"count": NT, "method_off": 5, "types": recs}, f, ensure_ascii=False)

print("\n[+] %s" % OUT_TXT)
print("[+] %s" % OUT_M)
print("[+] %s" % OUT_JSON)

print("\n[*] 抽查")
for want in ("System.String", "UnityEngine.GameObject", "MoleMole.BaseActor", "Mono.RuntimeStructs"):
    ns, _, tn = want.rpartition(".")
    hit = [r for r in recs if r["name"] == tn and r["ns"] == ns]
    if not hit:
        print("  %-32s 未找到" % want)
        continue
    r = hit[0]
    names = [MNAME.get(k, "?") for k in range(r["methodStart"], min(r["methodStart"] + r["methodCount"], r["methodStart"] + 6))]
    print("  %-32s start=%-6d count=%-4d %s" % (want, r["methodStart"], r["methodCount"], names))
