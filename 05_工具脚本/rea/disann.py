#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""disann.py  VA1 VA2 [--nohex]
反汇编任意区间，并把 rip 相对寻址 / 直接调用目标 解析成绝对 VA，附节名 + 可选解引用值。
"""
import struct
import sys

import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_pylibs"))
import capstone  # noqa: E402

PATH = r"Z:\AI\7.0\BH3_Data\Native\UserAssembly.dll"
IB = 0x180000000
d = open(PATH, "rb").read()

e = struct.unpack_from("<I", d, 0x3C)[0]
coff = e + 4
nsec = struct.unpack_from("<H", d, coff + 2)[0]
optsz = struct.unpack_from("<H", d, coff + 16)[0]
SECS = []
for i in range(nsec):
    o = coff + 20 + optsz + i * 40
    nm = d[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((nm, va, vs, rs, rp, o))


# ★ il2cpp 节头被清零（§9F.10），必须硬编码：rva 0x52E000 / raw 0x52CC00 / span 0x6727C00
IL2CPP = (0x052E000, 0x52CC00, 0x6727C00)


def va2off(va):
    rva = va - IB
    if IL2CPP[0] <= rva < IL2CPP[0] + IL2CPP[2]:
        return IL2CPP[1] + (rva - IL2CPP[0])
    for nm, sva, vs, rs, rp, _o in SECS:
        if sva <= rva < sva + max(vs, rs):
            if rp == 0:
                return None
            return rp + (rva - sva)
    return None


def secname(va):
    rva = va - IB
    if IL2CPP[0] <= rva < IL2CPP[0] + IL2CPP[2]:
        return "il2cpp"
    for nm, sva, vs, rs, rp, _o in SECS:
        if sva <= rva < sva + max(vs, rs):
            return nm
    return "?"


def rd32(va):
    o = va2off(va)
    if o is None:
        return None
    return struct.unpack_from("<I", d, o)[0]


def rd64(va):
    o = va2off(va)
    if o is None:
        return None
    return struct.unpack_from("<Q", d, o)[0]


def cstr(va, n=64):
    o = va2off(va)
    if o is None:
        return None
    b = d[o:o + n].split(b"\0")[0]
    try:
        s = b.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if len(s) < 2 or any(ord(c) < 0x20 or ord(c) == 0x7F for c in s):
        return None
    return s


def main():
    lo = int(sys.argv[1], 16)
    hi = int(sys.argv[2], 16)
    nohex = "--nohex" in sys.argv
    off = va2off(lo)
    if off is None:
        print("无映射")
        return
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    md.detail = True
    blob = d[off:off + (hi - lo)]
    for ins in md.disasm(blob, lo):
        ann = ""
        try:
            for op in ins.operands:
                if op.type == capstone.x86.X86_OP_MEM and op.mem.base == capstone.x86.X86_REG_RIP:
                    t = ins.address + ins.size + op.mem.disp
                    ann = "-> 0x%X [%s]" % (t, secname(t))
                    v = rd32(t)
                    if v is not None:
                        ann += " =0x%X/%d" % (v, v if v < 0x80000000 else v - 1 << 32)
                        s = cstr(t)
                        if s:
                            ann += ' "%s"' % s
                    break
                if op.type == capstone.x86.X86_OP_IMM and ins.mnemonic in ("call", "jmp"):
                    t = op.imm
                    ann = "-> 0x%X [%s]" % (t, secname(t))
                    break
        except Exception:
            pass
        hx = "" if nohex else ins.bytes.hex()
        print("  %X  %-24s %-34s %s" % (ins.address, hx, "%s %s" % (ins.mnemonic, ins.op_str), ann))


if __name__ == "__main__":
    main()
