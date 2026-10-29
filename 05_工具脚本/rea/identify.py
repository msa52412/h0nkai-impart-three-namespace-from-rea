#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""identify.py — 给一批 VA，打印「前 N 条指令 + 调用了谁 + 引用到的字符串」

用途：0x18042D860 这类 .text 里的运行时辅助函数没有符号，
但它们的调用频次极高（39 万次 / 12 万个调用者），必须先定名才能读懂调用图。
"""
import os
import re
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_pylibs"))
from capstone import Cs, CS_ARCH_X86, CS_MODE_64  # noqa: E402

DLL = r"Z:\AI\7.0\BH3_Data\Native\UserAssembly.dll"


def sections(data):
    e = struct.unpack_from("<I", data, 0x3C)[0]
    nsec = struct.unpack_from("<H", data, e + 6)[0]
    optsz = struct.unpack_from("<H", data, e + 20)[0]
    base = struct.unpack_from("<Q", data, e + 24 + 24)[0]
    sec = e + 24 + optsz
    out = []
    for i in range(nsec):
        o = sec + i * 40
        nm = data[o:o + 8].rstrip(b"\0").decode(errors="replace")
        vsz, va, rsz, rptr = struct.unpack_from("<IIII", data, o + 8)
        out.append((nm, va, max(vsz, rsz), rptr, rsz))
    return base, out


def main():
    data = open(DLL, "rb").read()
    base, secs = sections(data)

    def r2o(rva):
        for nm, va, span, rptr, rsz in secs:
            if va <= rva < va + span and rptr:
                return rptr + (rva - va), nm
        return None, None

    def cstr(va, n=64):
        off, nm = r2o(va - base)
        if off is None:
            return None
        raw = data[off:off + n].split(b"\0")[0]
        if len(raw) < 3 or any(c < 9 or (13 < c < 32) or c > 126 for c in raw):
            return None
        return raw.decode(errors="replace")

    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True

    for arg in sys.argv[1:]:
        va = int(arg, 16)
        off, sec = r2o(va - base)
        print("\n" + "=" * 78)
        print("VA 0x%X  节 %s  文件偏移 0x%X" % (va, sec, off if off else -1))
        if off is None:
            continue
        callees = []
        strs = []
        n = 0
        for ins in md.disasm(data[off:off + 400], va):
            print("  %08X  %-24s %s %s"
                  % (ins.address, ins.bytes.hex(" "), ins.mnemonic, ins.op_str))
            n += 1
            m = ins.mnemonic.lower()
            if m == "call" and ins.operands and ins.operands[0].type == 2:
                callees.append(ins.operands[0].imm)
            if m == "lea" and ins.operands and len(ins.operands) > 1 \
                    and ins.operands[1].type == 3 and ins.operands[1].mem.base == 0x29:
                t = ins.address + ins.size + ins.operands[1].mem.disp
                s = cstr(t)
                if s:
                    strs.append((t, s))
            if m in ("ret", "retn", "jmp") or n >= 26:
                break
        if callees:
            print("  -- call -> %s" % " ".join("0x%X" % c for c in callees))
        if strs:
            print("  -- 字符串 -> %s" % ", ".join("%r@0x%X" % (s, t) for t, s in strs))


if __name__ == "__main__":
    main()
