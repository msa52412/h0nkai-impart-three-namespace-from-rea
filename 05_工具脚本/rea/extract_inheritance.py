#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
继承树终局：Il2CTYPE 表在 DLL .rdata 静态区
  指针表 0x186D41F80 (PTR_PTR_1881a3628 初值)
  条目 12 字节: {u32 data; pad6; u8 type@10; u8 bits@11}

对每个类型:
  parentIdx -> 指针表[idx] -> 条目.data (type 0x11/0x12/0x1C) = 父 typedef 索引
  byvalIdx  -> 同理，data 应 == 自身索引（自检锚点）
"""
import struct
from collections import Counter, defaultdict

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
OUT_TXT = r"D:\Carol-start\_rea\bh3_types_full.txt"
OUT_TREE = r"D:\Carol-start\_rea\bh3_inheritance.txt"

BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x5C
NT = 57487
TBL_VA = 0x186D41F80

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
    name = d[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((name, va, vs, rs, rp))


def va2off(va):
    rva = va - IB
    for name, vaddr, vsize, rsize, rptr in SECS:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return None if rsize == 0 else rptr + (rva - vaddr)
    return None


def u32va(va):
    o = va2off(va)
    return None if o is None else struct.unpack_from("<I", d, o)[0]


# ---------- 指针表长度探测 ----------
tbl_off = va2off(TBL_VA)
print("指针表文件偏移 0x%X" % tbl_off)
N_PTR = 0
lo, hi = 0x186C56000, 0x188D09E64  # .rdata 范围
i = 0
while True:
    p = struct.unpack_from("<Q", d, tbl_off + i * 8)[0]
    if not (lo <= p < hi):
        break
    i += 1
    if i > 600000:
        break
N_PTR = i
print("指针表条目数 = %d (0x%X), 末指针 0x%X" % (N_PTR, N_PTR, struct.unpack_from("<Q", d, tbl_off + (N_PTR - 1) * 8)[0]))

# ---------- metadata 类型表 ----------
TYPE_OFF = (u32va(0x188198E08) ^ 0x2B849DB3) & M32
POOL_OFF = u32va(0x188198E50) ^ 0x7483FF7A
K_MUL = (-0x394A88E12FFFF3A0) & M64
K_ADD = 0x53DB1FC7E9ECC644
K_STEP = 0x64C7CE0352814CF6
BUF = open(META, "rb").read()
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
S16 = [(SALT[i] & 0xFFFF) - 0x10000 if SALT[i] & 0x8000 else (SALT[i] & 0xFFFF) for i in range(NT)]

_sc = {}


def dec(pid):
    if pid in _sc:
        return _sc[pid]
    L = (pid >> 24) & 0xFF
    if L == 0 or L > 0x80:
        _sc[pid] = None
        return None
    ix = pid & 0xFFFFFF
    src = P_ABS + ix
    nb = (L + 7) >> 3
    if src + nb * 8 > FSIZE:
        _sc[pid] = None
        return None
    key = (ix * K_MUL + K_ADD) & M64
    out = bytearray()
    for b in range(nb):
        out += (_U64.unpack_from(BUF, src + b * 8)[0] ^ key).to_bytes(8, "little")
        key = (key + K_STEP) & M64
    try:
        t = out[:L].decode("utf-8")
    except UnicodeDecodeError:
        _sc[pid] = None
        return None
    for ch in t:
        if ord(ch) < 0x20 or ord(ch) == 0x7F:
            _sc[pid] = None
            return None
    _sc[pid] = t
    return t


recs = []
for i in range(NT):
    off = T0 + i * STEP
    r = struct.unpack_from("<23I", BUF, off)
    s = SALT[i]
    name = dec((((r[13] ^ 0x3399EFB) - s) & M32))
    ns = dec(((((r[12] - s) & M32) - 0x4B6ACCC7) & M32)) or ""
    par = ((r[0] - 0x15F045CB) - s) & M32
    byv = ((r[10] - 0x67AD6F69) - s) & M32
    ms = ((r[5] - 0x2822B502) - s) & M32
    r16 = struct.unpack_from("<H", BUF, off + 0x48)[0]
    s16r = r16 - 0x10000 if r16 & 0x8000 else r16
    mc = (s16r + 0x1950 - S16[i]) & 0xFFFF
    r16n = struct.unpack_from("<H", BUF, off + 0x46)[0]
    nc = ((r16n ^ 0x7883) - S16[i]) & 0xFFFF
    tok = ((r[22] ^ 0x78647F39) - s) & M32
    recs.append({"i": i, "ns": ns, "name": name, "par": par, "byval": byv,
                 "ms": -1 if ms == M32 else ms, "mc": mc, "nc": nc, "tok": tok})


def full(i):
    return (recs[i]["ns"] + "." if recs[i]["ns"] else "") + (recs[i]["name"] or "?")


# ---------- Il2CTYPE 解析 ----------
def ctype_data(idx):
    """返回 (data, type) 或 None"""
    if idx < 0 or idx >= N_PTR:
        return None
    p = struct.unpack_from("<Q", d, tbl_off + idx * 8)[0]
    po = va2off(p)
    if po is None:
        return None
    return struct.unpack_from("<I", d, po)[0], d[po + 10]


# 自检：byval[idx] 的 data 应 == 自身 typedef 索引
ok_byv = bad_byv = 0
for i in range(NT):
    b = recs[i]["byval"]
    c = ctype_data(b)
    if c and c[0] == i:
        ok_byv += 1
    else:
        bad_byv += 1
print("\n[byval 自检] data==自身: %d / 不符: %d" % (ok_byv, bad_byv))

# parent 解析
TYPECLASS = {0x11, 0x12, 0x1C}
solved = complex_ = nil_ = badidx = 0
for rec in recs:
    p = rec["par"]
    if p == M32 or p < 0:
        rec["parent_full"] = ""
        nil_ += 1
        continue
    c = ctype_data(p)
    if c is None:
        rec["parent_full"] = "<bad idx %d>" % p
        badidx += 1
        continue
    data, ty = c
    if ty in TYPECLASS and data < NT:
        rec["parent_full"] = full(data)
        rec["parent_idx"] = data
        solved += 1
    else:
        rec["parent_full"] = "<type 0x%02X idx %d>" % (ty, p)
        complex_ += 1
print("[parent 解析] 类引用直接解: %d / 复杂类型: %d / nil: %d / 坏索引: %d"
      % (solved, complex_, nil_, badidx))

# 验证锚点
print("\n[锚点验证]")
for t, want in (("System.String", "System.Object"), ("System.Exception", "System.Object"),
                ("System.Int32", "System.ValueType"), ("System.Enum", "System.ValueType"),
                ("UnityEngine.GameObject", "UnityEngine.Object"), ("System.Object", "")):
    ns, _, tn = t.rpartition(".")
    r = next((x for x in recs if x["name"] == tn and x["ns"] == ns), None)
    got = r["parent_full"] if r else "<未找到>"
    print("  %-28s -> %-32s %s" % (t, got, "OK" if got == want else "期望 %s" % want))

# 输出 v3
with open(OUT_TXT, "w", encoding="utf-8") as f:
    f.write("index\tnamespace\ttype\ttoken\tmethodStart\tmethodCount\tnestedCount\tparentIdx\tparent\n")
    for r in recs:
        f.write("%d\t%s\t%s\t%08X\t%d\t%d\t%d\t%d\t%s\n"
                % (r["i"], r["ns"], r["name"] or "", r["tok"], r["ms"], r["mc"], r["nc"],
                   -1 if r["par"] == M32 else r["par"], r.get("parent_full", "")))
print("\n[+] %s (v3)" % OUT_TXT)

# 继承树统计 + 输出
children = defaultdict(list)
for r in recs:
    if r.get("parent_idx") is not None:
        children[r["parent_idx"]].append(r["i"])

with open(OUT_TREE, "w", encoding="utf-8") as f:
    # 按父类分组输出
    for pi in sorted(children, key=lambda k: -len(children[k])):
        f.write("\n### %s  (%d 个子类)\n" % (full(pi), len(children[pi])))
        for ci in children[pi][:400]:
            f.write("    %s\n" % full(ci))
print("[+] %s" % OUT_TREE)

print("\n[父类频次 Top 12]")
c = Counter(r["parent_full"] for r in recs if r.get("parent_full") and not r["parent_full"].startswith("<"))
for k, v in c.most_common(12):
    print("  %-42s %6d" % (k, v))

# 深度链验证
print("\n[最深继承链]")
def depth(i, seen=None):
    if seen is None:
        seen = set()
    if i in seen or i >= NT:
        return 0
    seen.add(i)
    p = recs[i].get("parent_idx")
    if p is None:
        return 1
    return 1 + depth(p, seen)

deep = sorted(range(NT), key=lambda i: -depth(i))[:5]
for i in deep:
    chain = []
    j = i
    for _ in range(20):
        chain.append(full(j))
        pj = recs[j].get("parent_idx")
        if pj is None:
            break
        j = pj
    print("  (%d) %s" % (depth(i), " -> ".join(chain[:8])))
