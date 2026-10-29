#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在 .text 里定位引用指定全局变量的指令，并用 .pdata 反查所属函数。

RIP 相对寻址判定：ModRM 的 mod=00, rm=101 (即 ModRM == 0x05)
    指令结束地址 + disp32 = 目标 VA
"""
import struct
import bisect

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"

# 要找的全局（VA）
TARGETS = {
    0x1881A3628: "PTR_PTR_1881a3628 (Il2CTYPE 指针表)",
    0x1881A35F0: "PTR_PTR_1881a35f0 (类型辅助表)",
}

with open(DLL, "rb") as f:
    data = f.read()

e = struct.unpack_from("<I", data, 0x3C)[0]
coff = e + 4
nsec = struct.unpack_from("<H", data, coff + 2)[0]
optsz = struct.unpack_from("<H", data, coff + 16)[0]
opt = coff + 20
IB = struct.unpack_from("<Q", data, opt + 24)[0]

secs = {}
sh = opt + optsz
for i in range(nsec):
    o = sh + i * 40
    name = data[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", data, o + 8)
    secs[name] = (va, vs, rs, rp)

t_va, t_vs, t_rs, t_rp = secs[".text"]
TEXT = data[t_rp:t_rp + t_rs]
TEXT_VA = IB + t_va
print(".text: VA 0x%X, %d 字节" % (TEXT_VA, len(TEXT)))

# ---- .pdata 建函数表 ----
p_va, p_vs, p_rs, p_rp = secs[".pdata"]
nfunc = p_rs // 12
begins = []
for i in range(nfunc):
    b = struct.unpack_from("<I", data, p_rp + i * 12)[0]
    begins.append(b)
order = sorted(range(nfunc), key=lambda i: begins[i])
sorted_begins = [begins[i] for i in order]
print(".pdata: %d 个函数条目" % nfunc)


def func_of(rva):
    k = bisect.bisect_right(sorted_begins, rva) - 1
    if k < 0:
        return None
    return sorted_begins[k]


# ---- 扫描 ----
# 单字节 opcode（会写/读 [rip+x]）
OPS1 = {0x8B, 0x8D, 0x89, 0x39, 0x3B, 0x03, 0x2B, 0x01, 0x85, 0x0F}
results = {va: [] for va in TARGETS}

n = len(TEXT)
for i in range(n - 8):
    b0 = TEXT[i]
    if 0x48 <= b0 <= 0x4F:          # REX 前缀
        op = TEXT[i + 1]
        modrm = TEXT[i + 2]
        if modrm != 0x05:
            continue
        if op not in (0x8B, 0x8D, 0x89, 0x39, 0x3B, 0x03, 0x2B, 0x01, 0x85):
            continue
        end = i + 7
        disp = struct.unpack_from("<i", TEXT, i + 3)[0]
    else:
        op = b0
        modrm = TEXT[i + 1]
        if modrm != 0x05:
            continue
        if op not in (0x8B, 0x8D, 0x89, 0x39, 0x3B, 0x03, 0x2B, 0x01, 0x85):
            continue
        end = i + 6
        disp = struct.unpack_from("<i", TEXT, i + 2)[0]
    target = TEXT_VA + end + disp
    if target in results:
        results[target].append((TEXT_VA + i, op, b0))

for va, desc in TARGETS.items():
    hits = results[va]
    funcs = {}
    for addr, op, b0 in hits:
        rva = addr - IB
        fb = func_of(rva)
        funcs.setdefault(fb, []).append(addr)
    print("\n" + "=" * 78)
    print("%s  (0x%X)" % (desc, va))
    print("  引用指令 %d 处，分布在 %d 个函数" % (len(hits), len(funcs)))
    for fb, addrs in sorted(funcs.items()):
        if fb is None:
            print("    <无函数>  " + ", ".join("0x%X" % a for a in addrs[:6]))
        else:
            print("    FUN_%X  (函数内 %d 处)  %s" %
                  (IB + fb, len(addrs), ", ".join("0x%X" % a for a in addrs[:6])))
