# -*- coding: utf-8 -*-
"""反汇编指定 VA 附近代码。"""
import sys, struct
sys.path.insert(0, r"D:\Carol-start\_rea")
from peutil import PE
import capstone

# 游戏代码在 UserAssembly.dll 的 il2cpp 节里（rva 0x52E000 起）。
# 早期这里写的是 UnityPlayer.dll（只有 28MB，.text 到 rva 0x14CC0CA 就结束），
# 拿它解析 0x18xxxxxxx 会落进 .rdata，反汇编出一堆垃圾指令，已修正。
DLL = r"D:\BH3\7.0\BH3_Data\Native\UserAssembly.dll"


def disasm(va, before=0x120, after=0x180, pe=None, annotate=True):
    pe = pe or PE(DLL)
    start = va - before
    off = pe.va2off(start)
    code = pe.data[off:off + before + after]
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    md.detail = True
    for ins in md.disasm(code, start):
        mark = "  <<<<" if ins.address == va else ""
        line = "0x%X  %-22s %s %s%s" % (ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str, mark)
        if annotate:
            # 解析 RIP 相对操作数，标注指向的字符串
            for op in ins.operands:
                if op.type == capstone.x86.X86_OP_MEM and op.mem.base == capstone.x86.X86_REG_RIP:
                    tgt = ins.address + ins.size + op.mem.disp
                    s = read_cstr(pe, tgt)
                    if s:
                        line += "      ; \"%s\"" % s[:60]
        print(line)


def read_cstr(pe, va, maxlen=90):
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


if __name__ == "__main__":
    va = int(sys.argv[1], 16) if len(sys.argv) > 1 else 0x180D55935
    b = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x120
    a = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x180
    disasm(va, b, a)
