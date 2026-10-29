# -*- coding: utf-8 -*-
"""验证方法记录 +0x00（声明类型）与 +0x08（返回类型）两列的变换。"""
import struct

M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
BASE = 0x118
T = 0xFA8318
N = 408461
NTYPE = 57487
NCTYPE = 354184

buf = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()


def prf_m(i):
    t = ((i * 0xB069) & M64) ^ 0x3E382F2D
    t = (t * 0x24147491) & M64
    t = (t ^ 0xF997B4A800) & M64
    t = t >> 10
    t = (t * 0x3857AACA) & M64
    return (t >> 0xE) & M32


def dec_type(i, off, const):
    raw = struct.unpack_from("<I", buf, BASE + T + i * 0x20 + off)[0]
    return ((raw + const) & M32) ^ prf_m(i)


print("[1] rec[0] -> 声明类型  (const 0xE5AF14B4)")
decl = []
bad = 0
for i in range(N):
    v = dec_type(i, 0, 0xE5AF14B4)
    decl.append(v)
    if v >= NCTYPE:
        bad += 1
print("    越界(<%d) 个数 = %d (%.4f%%)" % (NCTYPE, bad, 100.0 * bad / N))
print("    范围 %d .. %d" % (min(decl), max(decl)))

# 单调性：方法按声明类型排序，类型索引应非降
nondec = sum(1 for i in range(1, N) if decl[i] < decl[i - 1])
print("    非降违反次数 = %d" % nondec)

# 每类型方法数 vs typedef +0x48
print("\n[2] 与 typedef.methodCount 对照")
SALT = [struct.unpack_from("<I", buf, BASE + i * 0x5C)[0] for i in range(NTYPE)]
S16 = [(s & 0xFFFF) - 0x10000 if s & 0x8000 else (s & 0xFFFF) for s in SALT]


def ptype(i):
    t = ((i * 0x1F17946EF935 + 0xAFD81BAECAFDAC6) & M64) >> 0x15
    t = (t + 0x54760499) & M64
    t = (t * 0x1125F1B6) & M64
    return t & 0xFFFF


cnt = [0] * NTYPE
for v in decl:
    if v < NTYPE:
        cnt[v] += 1
ok = bad2 = 0
for i in range(NTYPE):
    raw16 = struct.unpack_from("<H", buf, BASE + i * 0x5C + 0x48)[0]
    c = ((raw16 + 0x1950) & 0xFFFF) ^ ptype(i)
    if c == cnt[i]:
        ok += 1
    elif c != 0 or cnt[i] != 0:
        bad2 += 1
print("    方法数一致类型 = %d / %d   (不一致 %d)" % (ok, NTYPE, bad2))
print("    解出方法总数 = %d" % sum(cnt))

print("\n[3] rec[8] -> 返回类型  (const 0xAEAE5FEE)")
ret = [dec_type(i, 8, 0xAEAE5FEE) for i in range(N)]
rv = [v for v in ret if v != M32]
print("    void(0xFFFFFFFF) = %d   非 void = %d" % (N - len(rv), len(rv)))
oor = [v for v in rv if v >= NCTYPE]
print("    越界(<%d) = %d (%.4f%%)" % (NCTYPE, len(oor), 100.0 * len(oor) / max(1, len(rv))))
print("    非 void 范围 %d .. %d" % (min(rv), max(rv)) if rv else "    -")

print("\n[4] 抽样：前 6 条方法")
def full_type(ti):
    return ti
for i in list(range(6)) + [22599, 22600, 22601]:
    d = decl[i]
    r = ret[i]
    print("    i=%-6d decl=%-7d ret=%-8s" % (i, d, "void" if r == M32 else r))

print("\n[5] 保存中间结果供后续使用")
import json
with open("_diag_method_cols.json", "w") as f:
    json.dump({"decl_sample": decl[:50], "ret_sample": [("v" if x == M32 else x) for x in ret[:50]]}, f)
