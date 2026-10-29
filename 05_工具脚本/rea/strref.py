# -*- coding: utf-8 -*-
"""解析 RIP 相对操作数指向的 il2cpp 字符串字面量。

il2cpp String 对象布局:
    +0x00 klass
    +0x08 monitor
    +0x10 length (int32)
    +0x14 UTF-16LE chars

用法:
    python strref.py 0x183506600 0x120      # 反汇编该区间，逐个解 RIP 相对引用
"""
import sys, os, struct
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from peutil import PE
import capstone

DLL = r"D:\BH3\7.0\BH3_Data\Native\UserAssembly.dll"


def read_cstr(pe, va, n=120):
    off = pe.va2off(va)
    if off is None:
        return None
    seg = pe.data[off:off + n]
    e = seg.find(b"\x00")
    if e < 4:
        return None
    try:
        s = seg[:e].decode("utf-8")
    except UnicodeDecodeError:
        return None
    return s if all(32 <= ord(c) < 127 for c in s) else None


def read_qword(pe, va):
    off = pe.va2off(va)
    if off is None:
        return None
    return struct.unpack_from("<Q", pe.data, off)[0]


def read_il2cpp_string(pe, obj_va, maxlen=200):
    """obj_va 指向 String 对象本体。"""
    off = pe.va2off(obj_va)
    if off is None:
        return None
    n = struct.unpack_from("<i", pe.data, off + 0x10)[0]
    if not (0 < n <= maxlen):
        return None
    raw = pe.data[off + 0x14: off + 0x14 + n * 2]
    try:
        return raw.decode("utf-16-le")
    except UnicodeDecodeError:
        return None


def resolve_literal(pe, va):
    """先试直接 C 字符串，再试「qword 指向 String 对象」。"""
    s = read_cstr(pe, va)
    if s:
        return s, "cstr"
    p = read_qword(pe, va)
    if p:
        s = read_il2cpp_string(pe, p)
        if s:
            return s, "il2cpp"
    return None, None


def main():
    va = int(sys.argv[1], 16)
    span = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x100
    pe = PE(DLL)
    off = pe.va2off(va)
    code = pe.data[off:off + span]
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    md.detail = True
    for ins in md.disasm(code, va):
        ann = ""
        for op in ins.operands:
            if op.type == capstone.x86.X86_OP_MEM and op.mem.base == capstone.x86.X86_REG_RIP:
                tgt = ins.address + ins.size + op.mem.disp
                s, kind = resolve_literal(pe, tgt)
                if s:
                    ann += '   ; [%s] "%s"' % (kind, s)
                else:
                    ann += "   ; -> %#x" % tgt
        print("0x%X  %-20s %-7s %-30s%s"
              % (ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str, ann))


if __name__ == "__main__":
    main()
