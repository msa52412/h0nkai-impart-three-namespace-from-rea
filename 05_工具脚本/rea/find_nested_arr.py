#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定位 nestedTypes 数组在 metadata 文件中的位置。

已知（强约束，非猜测）：
  · 数组长度 = 21429，是连续的 TypeDefinitionIndex 段
  · 每个父类型占据 [nestedStart, nestedStart+nestedCount)
  · 10390 个父类型唯一 start 值，零重叠零空洞，末值恰好 21429
  · 数组元素必然是「嵌套类型」，而嵌套类型 TypeDef 的 namespace 按 ECMA 必为空
    -> 每个元素都必须在「空 namespace 类型索引集合」内（21994 个）

判据：窗口内 21429 个元素**全部**命中该集合。随机命中率 ≈ 0。
"""
import struct, time, sys

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
TYPES = r"D:\Carol-start\_rea\bh3_types_v5.txt"

BASE = 0x118
M32 = 0xFFFFFFFF
NT = 57487
NEED = 21429

dll = open(DLL, "rb").read()
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
BUF = open(META, "rb").read()
T0 = BASE + TYPE_OFF
FS = len(BUF)

rows = [l.rstrip("\n").split("\t") for l in open(TYPES, encoding="utf-8")][1:]
empt = set(int(r[0]) for r in rows if len(r) >= 10 and r[1] == "")
print("空 namespace 类型 %d 个" % len(empt))

ok = bytearray(NT + 1)
for x in empt:
    if x < NT:
        ok[x] = 1
okb = bytes(ok)


def scan(width, step):
    """width=4/2；返回命中偏移列表"""
    fmt = "I" if width == 4 else "H"
    mv = memoryview(BUF)[: (FS // width) * width].cast(fmt)
    n = len(mv)
    span = NEED
    hits = []
    t = time.time()
    limit = n - span
    i = 0
    checked = 0
    while i < limit:
        a = mv[i]
        b = mv[i + span - 1]
        if a < NT and okb[a] and b < NT and okb[b]:
            checked += 1
            j = i
            end = i + span
            good = True
            while j < end:
                v = mv[j]
                if v >= NT or not okb[v]:
                    good = False
                    break
                j += 1
            if good:
                hits.append(i * width)
                print("  命中 %d 位 @ 0x%X (i=%d)" % (width * 8, i * width, i))
        i += step // width if step >= width else 1
    print("%d 位扫描完毕 %.0f 秒，预筛通过 %d 处，命中 %d 处"
          % (width * 8, time.time() - t, checked, len(hits)))
    return hits


print("\n[*] 32 位窗口")
h4 = scan(4, 4)
print("\n[*] 16 位窗口")
h2 = scan(2, 2)
print("\n结果：32位=%s  16位=%s" % (h4, h2))
