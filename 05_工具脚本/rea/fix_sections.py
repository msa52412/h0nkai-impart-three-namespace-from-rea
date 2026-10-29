#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix_sections.py — 修复两处反分析伪装，生成可被 Ghidra/IDA 正常装载的副本

实测到的两处篡改：
  1) il2cpp 节头被清零
       .text   VA 0x001000 VSize 0x52C7E6 RawPtr 0x000400 RawSize 0x52C800  （真实）
       il2cpp  VA 0x52E000 VSize 0x001000 RawPtr 0x000000 RawSize 0x000000  （伪装成空节）
       → IL2CPP 生成代码真实占据 VA 0x52E000..0x6C55C00，raw 自 0x52CC00 起
         （由 .pdata 的 Begin/End 校准：该区 raw = RVA - 0x1400，94.9% 函数体精确铺满）
  2) Exception 数据目录被指向 RVA 0x0ACF9000（无节声明的空洞），Size 0xABC1A4
       → 真实 .pdata 在节表中为 VA 0x09E85000 / VSize 0x0ABC930

本脚本只改 5 个节字段 + 1 个数据目录项，其余字节一律不动。
"""
import struct, sys, hashlib

SRC = sys.argv[1] if len(sys.argv) > 1 else "/home/nas/re/UserAssembly_slim.dll"
DST = sys.argv[2] if len(sys.argv) > 2 else "/home/nas/re/UserAssembly_fixed.dll"

NEW_VA     = 0x52E000
NEW_VSIZE  = 0x6727C00     # -> VA 0x6C55C00，覆盖 .pdata 最大 EndAddress 0x6C55B2A
NEW_RAWPTR = 0x52CC00
NEW_RAWSZ  = 0x6727C00     # -> raw 0x6C53800，不越过 .rdata 的 RawPtr 0x6C54800
CHARS      = 0x60000020    # CODE | EXECUTE | READ

d = bytearray(open(SRC, "rb").read())
print("源文件 %s  %d 字节" % (SRC, len(d)))

lf = struct.unpack_from("<I", d, 0x3C)[0]
coff = lf + 4
nsec = struct.unpack_from("<H", d, coff + 2)[0]
optsz = struct.unpack_from("<H", d, coff + 16)[0]
opt = coff + 20
print("nsec=%d optsz=%d SizeOfImage=0x%X"
      % (nsec, optsz, struct.unpack_from("<I", d, opt + 56)[0]))

il2cpp_off = None
pdata_va = pdata_vs = None
for i in range(nsec):
    o = opt + optsz + i * 40
    nm = bytes(d[o:o + 8]).rstrip(b"\x00").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    print("  [%2d] %-9s VA %08X VSize %08X RawPtr %08X RawSize %08X"
          % (i, nm, va, vs, rp, rs))
    if nm == "il2cpp":
        il2cpp_off = o
    if nm == ".pdata":
        pdata_va, pdata_vs = va, vs

if il2cpp_off is None:
    print("!! 未找到 il2cpp 节，放弃")
    sys.exit(1)
if pdata_va is None:
    print("!! 未找到 .pdata 节，放弃")
    sys.exit(1)

struct.pack_into("<I", d, il2cpp_off + 8, NEW_VSIZE)
struct.pack_into("<I", d, il2cpp_off + 12, NEW_VA)
struct.pack_into("<I", d, il2cpp_off + 16, NEW_RAWSZ)
struct.pack_into("<I", d, il2cpp_off + 20, NEW_RAWPTR)
struct.pack_into("<I", d, il2cpp_off + 36, CHARS)
print("已修正 il2cpp: VA %08X VSize %08X RawPtr %08X RawSize %08X -> VA end %08X"
      % (NEW_VA, NEW_VSIZE, NEW_RAWPTR, NEW_RAWSZ, NEW_VA + NEW_VSIZE))

dd = opt + 112
o_rva, o_sz = struct.unpack_from("<II", d, dd + 3 * 8)
struct.pack_into("<II", d, dd + 3 * 8, pdata_va, pdata_vs)
print("已修正 Exception 目录: %08X/%08X -> %08X/%08X"
      % (o_rva, o_sz, pdata_va, pdata_vs))

need = NEW_RAWPTR + NEW_RAWSZ
print("il2cpp raw 需至 %d，文件 %d 字节: %s"
      % (need, len(d), "OK" if len(d) >= need else "不足"))

open(DST, "wb").write(bytes(d))
print("已写出 %s  %d 字节  sha256=%s" % (DST, len(d), hashlib.sha256(bytes(d)).hexdigest()))
