# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from peutil import PE
import capstone

DLL = r"D:\BH3\7.0\BH3_Data\Native\UserAssembly.dll"
pe = PE(DLL)


def cstr(va, maxlen=100):
    off = pe.va2off(va)
    if off is None:
        return None
    seg = pe.data[off:off + maxlen]
    end = seg.find(b"\x00")
    if end < 4:
        return None
    try:
        s = seg[:end].decode("utf-8")
    except Exception:
        return None
    if not all(32 <= ord(c) < 127 for c in s):
        return None
    return s


def dis(rva, n=0x220):
    va = pe.image_base + rva
    off = pe.va2off(va)
    code = pe.data[off:off + n]
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    md.detail = True
    print("=== RVA %#x (VA %#x) ===" % (rva, va))
    for ins in md.disasm(code, va):
        line = "%#x  %-20s %s %s" % (ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str)
        for op in ins.operands:
            if op.type == capstone.x86.X86_OP_MEM and op.mem.base == capstone.x86.X86_REG_RIP:
                tgt = ins.address + ins.size + op.mem.disp
                s = cstr(tgt)
                if s:
                    line += "   ; \"%s\"" % s[:70]
                else:
                    line += "   ; -> %#x" % tgt
        print(line)
    print()


if __name__ == "__main__":
    for a in sys.argv[1:]:
        dis(int(a, 0))
