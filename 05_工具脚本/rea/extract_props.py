#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
属性表提取（完整版）

typedef +0x24 (SUB 0x97E219E0) = propertyStart
typedef +0x4A (SUB -0x17A3)   = property_count
typedef +0x48                 = methodStart（已在 v5 类型表中解出）
表基址 = buf + (u32(DAT_188198E28) ^ 0x3CB812E1) = 0x1C6766C, 记录 0x14

记录（经 FUN_18044ca90 汇编逐条核对，全部为 SUB EAX,EBP 形态）：
  [0] name     ^ 0x5566C15D   - m
  [4] getSlot  直接            - m    哨兵 0x4CF0C16A，槽位 = v - 0x4CF0C16B
  [8] token    直接            - m    再 -0x6F268466（≡ +0x90D97B9A），形如 0x1700000r
  [C] setSlot  ^ 0x0128B6C5   - m    哨兵 -1
  [10] attrs   ^ 0x72D0B1BB   - m    （本作全为 0）
其中 m = prfP(gi) * 0x1534FCF9，prfP = ((((gi*0x64D5)^0x6D7B1F20)+0x10ECA71E)*0x7737C996 >> 8) + 0x5505FF6B

关键结论：属性表本身【不含类型】。Il2CppPropertyInfo 结构与官方一致（无 type 域），
属性类型须由 getter 的返回类型给出。getSlot/setSlot 为类内方法槽，
全局方法索引 = typedef.methodStart + slot（已用 UnityEngine.Transform 全套验证）。
"""
import struct
import collections

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
OUT = r"D:\Carol-start\_rea\bh3_properties.tsv"
METHODS = r"D:\Carol-start\_rea\bh3_methods.txt"
TYPES = r"D:\Carol-start\_rea\bh3_types_v5.txt"

BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x5C
NT = 57487
TP = 0x1C6766C

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
TYPE_OFF = (u32va(0x188198E08) ^ 0x2B849DB3) & M32
POOL = u32va(0x188198E50) ^ 0x7483FF7A
T0 = BASE + TYPE_OFF
P = BASE + POOL
KM = (-0x394A88E12FFFF3A0) & M64
KA = 0x53DB1FC7E9ECC644
KS = 0x64C7CE0352814CF6
_u64 = struct.Struct("<Q")


def dec(pid):
    L = (pid >> 24) & 0xFF
    if L == 0:
        return None
    ix = pid & 0xFFFFFF
    src = P + ix
    nb = (L + 7) >> 3
    if src + nb * 8 > len(BUF):
        return None
    key = (ix * KM + KA) & M64
    out = bytearray()
    for b in range(nb):
        out += (_u64.unpack_from(BUF, src + b * 8)[0] ^ key).to_bytes(8, "little")
        key = (key + KS) & M64
    try:
        t = out[:L].decode("utf-8")
    except UnicodeDecodeError:
        return None
    for ch in t:
        if ord(ch) < 0x20 or ord(ch) == 0x7F:
            return None
    return t


SALT = []
for i in range(NT):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    SALT.append(((x * 0x1125F1B6) & M64) & M32)
S16 = [(SALT[i] & 0xFFFF) - 0x10000 if SALT[i] & 0x8000 else (SALT[i] & 0xFFFF) for i in range(NT)]

recs = []
for i in range(NT):
    off = T0 + i * STEP
    r = struct.unpack_from("<23I", BUF, off)
    s = SALT[i]
    nm = dec((((r[13] ^ 0x3399EFB) - s) & M32))
    ns = dec(((((r[12] - s) & M32) - 0x4B6ACCC7) & M32)) or ""
    ps = ((r[9] - s) + 0x97E219E0) & M32
    raw = struct.unpack_from("<H", BUF, off + 0x4A)[0]
    sr = raw - 0x10000 if raw & 0x8000 else raw
    pc = (sr + 0x17A3 - S16[i]) & 0xFFFF
    recs.append({"i": i, "ns": ns, "name": nm, "ps": ps, "pc": pc})


def full(i):
    return (recs[i]["ns"] + "." if recs[i]["ns"] else "") + (recs[i]["name"] or "?")


starts = {r["i"]: r["ps"] for r in recs if r["ps"] != M32}
tot = sum(r["pc"] for r in recs)
print("[属性] 有属性的类型 = %d / %d" % (len(starts), NT))
print("  propertyStart 范围 [%d, %d]  唯一 %d"
      % (min(starts.values()), max(starts.values()), len(set(starts.values()))))
print("  property_count 合计 = %d" % tot)
print("  建表区间(相对) = 0x%X .. 0x%X  (0x%X 字节)" % (TP, TP + tot * 0x14, tot * 0x14))

order = sorted(starts.items(), key=lambda kv: kv[1])
ok = bad = 0
for k in range(len(order) - 1):
    ti, st = order[k]
    if order[k + 1][1] - st == recs[ti]["pc"]:
        ok += 1
    else:
        bad += 1
print("  差分 vs +0x4A: 一致 %d / 不一致 %d" % (ok, bad))


def prfP(i):
    t = ((i * 0x64D5) & M64) ^ 0x6D7B1F20
    t = (t + 0x10ECA71E) & M64
    t = (t * 0x7737C996) & M64
    return (((t >> 8) & M32) + 0x5505FF6B) & M32


NAMEK = 0xEACB0307      # = -(0x1534FCF9) mod 2^32（汇编 IMUL RBP,RCX,0x1534fcf9 + SUB）

# ---- 外部联动表 ----
MSTART = {}
for line in open(TYPES, encoding="utf-8"):
    f = line.rstrip("\n").split("\t")
    if f[0].isdigit():
        MSTART[int(f[0])] = int(f[4])
MNAME = {}
for line in open(METHODS, encoding="utf-8"):
    f = line.rstrip("\n").split("\t")
    MNAME[int(f[0])] = f[3]

rows = []
for ti in sorted(starts):
    st = starts[ti]
    n = recs[ti]["pc"]
    tn = full(ti)
    ms0 = MSTART.get(ti, 0)
    for k in range(n):
        gi = st + k
        o = BASE + TP + gi * 0x14
        p0, p1, p2, p3, p4 = struct.unpack_from("<5I", BUF, o)
        m = (prfP(gi) * NAMEK) & M32
        nm = dec(((p0 ^ 0x5566C15D) + m) & M32) or ""
        g = (p1 + m) & M32
        tok = (((p2 + m) & M32) - 0x6F268466) & M32
        s = ((p3 ^ 0x0128B6C5) + m) & M32
        at = ((p4 ^ 0x72D0B1BB) + m) & M32
        gslot = "" if g == 0x4CF0C16A else (g - 0x4CF0C16B) & M32
        sslot = "" if s == M32 else s
        gidx = "" if gslot == "" else ms0 + gslot
        sidx = "" if sslot == "" else ms0 + sslot
        rows.append((ti, tn, gi, nm, "%08X" % tok, at,
                     gslot, "" if gidx == "" else "%d:%s" % (gidx, MNAME.get(gidx, "?")),
                     sslot, "" if sidx == "" else "%d:%s" % (sidx, MNAME.get(sidx, "?"))))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("typeIdx\ttypeName\tpropIdx\tpropName\ttoken\tattrs\tgetSlot\tgetter\tsetSlot\tsetter\n")
    for r in rows:
        f.write("\t".join(str(x) for x in r) + "\n")

print("\n[+] %s  (%d 条属性)" % (OUT, len(rows)))
print("  token 高字节 = %s   attrs 取值 = %s"
      % (dict(collections.Counter(r[4][:2] for r in rows)),
         dict(collections.Counter(r[5] for r in rows))))

# ---- 联名一致性验证 ----
cnt = hit = 0
miss = []
for r in rows:
    if not r[7]:
        continue
    cnt += 1
    getter = r[7].split(":", 1)[1]
    if getter == "get_" + r[3]:
        hit += 1
    elif len(miss) < 10:
        miss.append("%s.%s -> %s" % (r[1], r[3], getter))
print("\n[联名验证] 有 getter 的 %d 条中，getter 名 == 'get_'+属性名: %d (%.2f%%)"
      % (cnt, hit, 100.0 * hit / cnt))
if miss:
    print("  不一致样例（接口实现/显式实现属正常）:")
    for x in miss:
        print("    " + x)

print("\n[校验] 已知类型属性")
for t in ("System.String", "System.Exception", "UnityEngine.Transform",
          "System.Collections.Generic.List`1"):
    ti = next((r["i"] for r in recs if full(r["i"]) == t), None)
    if ti is None:
        continue
    sub = [r for r in rows if r[0] == ti]
    print("  %-40s %2d 属性" % (t, len(sub)))
    for r in sub[:5]:
        print("      %-22s tok=%s  %s  %s" % (r[3], r[4], r[7] or "-", r[9] or "-"))
