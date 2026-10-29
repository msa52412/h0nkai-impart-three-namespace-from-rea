#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stubpeek.py — 反汇编任意 VA 区间（本地 UserAssembly_slim.dll，RVA 与原文件一致）

用法：
    python stubpeek.py 0x1804fe000 0x1804fe500
    python stubpeek.py 0x1804fe000 0x1804fe500 --hexonly
"""
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_pylibs"))
from capstone import Cs, CS_ARCH_X86, CS_MODE_64  # noqa: E402

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
IMAGE_BASE = 0x180000000


def sections(data):
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    nsec = struct.unpack_from("<H", data, e_lfanew + 6)[0]
    optsz = struct.unpack_from("<H", data, e_lfanew + 20)[0]
    base = struct.unpack_from("<Q", data, e_lfanew + 24 + 24)[0]
    sec = e_lfanew + 24 + optsz
    out = []
    for i in range(nsec):
        o = sec + i * 40
        name = data[o:o + 8].rstrip(b"\0").decode(errors="replace")
        vsz, va, rsz, rptr = struct.unpack_from("<IIII", data, o + 8)
        out.append((name, va, max(vsz, rsz), rptr, rsz))
    return base, out


def rva2off(secs, rva):
    for name, va, span, rptr, rsz in secs:
        if va <= rva < va + span:
            if rptr == 0:
                return None, name          # raw 被摘掉
            return rptr + (rva - va), name
    return None, None


def main():
    lo = int(sys.argv[1], 16)
    hi = int(sys.argv[2], 16)
    hexonly = "--hexonly" in sys.argv
    data = open(DLL, "rb").read()
    base, secs = sections(data)
    print("ImageBase=0x%X  %s" % (base, os.path.basename(DLL)))
    print("%-9s %-9s %-9s %-9s %s" % ("节", "RVA", "VSize", "RawPtr", "RawSize"))
    for name, va, span, rptr, rsz in secs:
        print("%-9s 0x%08X 0x%08X 0x%08X 0x%08X" % (name, va, span, rptr, rsz))
    print()

    off, secname = rva2off(secs, lo - base)
    if off is None:
        print("0x%X 无法映射（节 %s）" % (lo, secname))
        return
    blob = data[off:off + (hi - lo)]
    print("=== 0x%X..0x%X  节 %s  文件偏移 0x%X  共 %d 字节 ==="
          % (lo, hi, secname, off, len(blob)))
    for row in range(0, len(blob), 16):
        chunk = blob[row:row + 16]
        print("  %08X  %-47s  %s" % (lo + row, chunk.hex(" "),
                                     "".join(chr(c) if 32 <= c < 127 else "." for c in chunk)))
    if hexonly:
        return

    print("\n=== 逐函数反汇编（遇 jmp/ret/int3 断界）===")
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = False
    va = lo
    end = hi
    while va < end:
        if blob[va - lo:va - lo + 1] == b"\xcc":
            va += 1
            continue
        n = 0
        stop = False
        lines = []
        nextva = va
        for ins in md.disasm(blob[va - lo:], va):
            lines.append("    %08X  %-22s %s %s"
                         % (ins.address, ins.bytes.hex(" "), ins.mnemonic, ins.op_str))
            nextva = ins.address + ins.size
            n += 1
            m = ins.mnemonic.lower()
            if m in ("ret", "retn", "jmp", "int3", "hlt", "ud2"):
                stop = True
                break
            if n >= 40:
                break
        if not lines:
            print("  %08X  <?>" % va)
            va += 1
            continue
        print("  --- 0x%X （%d 字节）---" % (va, nextva - va))
        print("\n".join(lines))
        va = nextva if nextva > va else va + 1
        if stop and va < end and blob[va - lo] == 0xCC:
            va += 1


if __name__ == "__main__":
    main()
