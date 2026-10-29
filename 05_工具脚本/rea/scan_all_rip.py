#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全量扫描 .text 中所有指向 0x1881A3628 的 RIP 相对指令（不限 ModRM=0x05）
覆盖:
  mov reg,[rip+d]   48 8B 05..3D / 8B 05..3D
  lea reg,[rip+d]   48 8D 05..3D / 8D 05..3D
  mov [rip+d],reg   48 89 05..3D / 89 05..3D
  mov r/m 操作数位置在 ModRM 其它编码下的（扫 disp32 对齐窗口）
思路：对每个候选位置 i，若 [i-3..i+8] 窗口内任一 RIP 相对解码命中目标，输出。
简化：检查字节 i 处 48 8B/48 8D/48 89/8B/8D/89 + ModRM(05,0D,15,1D,25,2D,35,3D)
      disp32 在 i+2/i+3，目标 = i+len+disp32
"""
import struct
import bisect

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
TARGETS = {0x1881A3628, 0x1881A35F0}

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

p_va, p_vs, p_rs, p_rp = secs[".pdata"]
nfunc = p_rs // 12
begins = []
for i in range(nfunc):
    b, en = struct.unpack_from("<II", data, p_rp + i * 12)
    begins.append(b)
order = sorted(range(nfunc), key=lambda i: begins[i])
sb = [begins[i] for i in order]


def func_of(rva):
    k = bisect.bisect_right(sb, rva) - 1
    if k < 0:
        return None
    return sb[k] if rva - sb[k] < 0x8000 else None


hits = []
n = len(TEXT)
i = 0
MODRM = {0x05, 0x0D, 0x15, 0x1D, 0x25, 0x2D, 0x35, 0x3D}
while i < n - 7:
    b0 = TEXT[i]
    if b0 == 0x48:
        op, moff = TEXT[i + 1], 2
    elif b0 in (0x4C,):
        op, moff = TEXT[i + 1], 2
    elif b0 in (0x8B, 0x8D, 0x89, 0xC7):
        op, moff = b0, 0
    else:
        i += 1
        continue
    if op not in (0x8B, 0x8D, 0x89, 0xC7):
        i += 1
        continue
    if b0 == 0x48 and TEXT[i + 1] != op:
        pass
    modrm = TEXT[i + moff]
    if modrm in MODRM:
        disp = struct.unpack_from("<i", TEXT, i + moff + 1)[0]
        ilen = moff + 5
        tgt = TEXT_VA + i + ilen + disp
        if tgt in TARGETS:
            hits.append((TEXT_VA + i, b0, op, modrm))
        i += 1
    else:
        i += 1

print("命中 %d 条" % len(hits))
byfunc = {}
for va, b0, op, modrm in hits:
    fb = func_of(va - IB)
    byfunc.setdefault(fb, []).append((va, b0, op, modrm))

OPN = {0x8B: "mov r,[rip]", 0x8D: "lea r,[rip]", 0x89: "mov [rip],r", 0xC7: "mov [rip],imm"}
for fb, lst in sorted(byfunc.items(), key=lambda kv: -len(kv[1])):
    print("\nFUN_%X  %d 处:" % (IB + (fb or 0), len(lst)))
    for va, b0, op, modrm in lst[:8]:
        print("   0x%X  %s  prefix=%02X" % (va, OPN[op], b0))
