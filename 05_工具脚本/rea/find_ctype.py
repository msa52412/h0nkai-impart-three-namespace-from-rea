#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1) dump DAT_188198E00-E98 全部常量（相对已知段的距离关系）
2) 在 [类型表尾, 方法表头] 之间扫 Il2CTYPE 表（明文假设，12 字节条目）
"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
BASE = 0x118
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
            return None if rsize == 0 else struct.unpack_from("<I", dll, rptr + (rva - vaddr))[0]
    return None


print("[DAT_188198E00-E98 常量]")
known = {0x512A0: "类型表", 0xFA8318: "方法表", 0x24AAC18: "字符串池", 0x1C2A198: "表5(程序集)",
         0x1C41E98: "数组C(嵌套)", 0x1C56D6C: "数组B", 0x1C57D10: "数组A"}
for g in range(0x188198E00, 0x188198EA0, 4):
    v = u32va(g)
    print("  DAT_%x = 0x%08X (%d)" % (g, v, v))

BUF = open(META, "rb").read()
FS = len(BUF)
print("\n文件大小 = 0x%X" % FS)

# 已知段边界
type_end = BASE + 0x512A0 + 57487 * 0x5C
meth_beg = BASE + 0xFA8318
print("类型表尾 = 0x%X, 方法表头 = 0x%X, 空隙 = %.1f MB"
      % (type_end, meth_beg, (meth_beg - type_end) / 1048576))

# Il2CTYPE 明文扫描：条目 {u32 data; u32 pad?; ...; byte@10 type}
print("\n[Il2CTYPE 明文扫描]  区域 [0x%X, 0x%X]" % (type_end, meth_beg))
NT = 57487
best = []
for step in (12, 16, 8):
    ok = 0
    n = 0
    off0 = None
    for off in range(type_end, min(type_end + 0x40000, meth_end := meth_beg) - step, step):
        data = struct.unpack_from("<I", BUF, off)[0]
        ty = BUF[off + 10]
        n += 1
        if data < NT and 1 <= ty <= 0x1E:
            ok += 1
            if off0 is None:
                off0 = off
    print("  步长 %-3d: 合法条目 %d/%d (%.1f%%)  首个合法 @ 0x%X"
          % (step, ok, n, 100.0 * ok / max(n, 1), off0 or 0))
    best.append((ok / max(n, 1), step, off0))

# 全区域滚动扫描（找合法率最高的起点，步长 12）
print("\n[滚动定位] 步长 12，按 0x1000 窗口统计合法率")
step = 12
bestwin = None
for w0 in range(type_end, meth_beg - 0x1000, 0x1000):
    ok = tot = 0
    for off in range(w0, w0 + 0x1000 - step, step):
        data = struct.unpack_from("<I", BUF, off)[0]
        ty = BUF[off + 10]
        tot += 1
        if data < NT and 1 <= ty <= 0x1E:
            ok += 1
    r = ok / max(tot, 1)
    if bestwin is None or r > bestwin[0]:
        bestwin = (r, w0, ok, tot)
print("  最佳窗口: 合法率 %.1f%% @ 0x%X (%d/%d)"
      % (bestwin[0] * 100, bestwin[1], bestwin[2], bestwin[3]))
# 从最佳起点向后连续检查
r, w0, _, _ = bestwin
n = 0
while True:
    off = w0 + n * step
    if off + step > FS:
        break
    data = struct.unpack_from("<I", BUF, off)[0]
    ty = BUF[off + 10]
    if not (data < NT or data == M32) or not (1 <= ty <= 0x1E):
        break
    n += 1
print("  从 0x%X 连续合法条目 = %d (0x%X 字节)" % (w0, n, n * step))
if n > 1000:
    print("\n  [样本] 前 8 条:")
    for k in range(8):
        off = w0 + k * step
        data, = struct.unpack_from("<I", BUF, off)
        print("    +%d: data=%-7d type=0x%02X attrs=0x%04X" % (k, data, BUF[off + 10], struct.unpack_from("<H", BUF, off + 8)[0]))
    print("  [索引 200000 附近] (byval 区):")
    for k in range(209547 - 3, 209547 + 3):
        off = w0 + k * step
        data, = struct.unpack_from("<I", BUF, off)
        print("    [%d]: data=%-7d type=0x%02X" % (k, data, BUF[off + 10]))
