# -*- coding: utf-8 -*-
"""带符号解析的反汇编器：把 call/jmp 目标翻译成 C# 方法名。

用法:
    python fn.py 0x182D02CE0 [条数]
"""
import sys, re, os, glob, json, struct
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)          # peutil.py 就在本目录
from peutil import PE
import capstone

DLL = r"D:\BH3\7.0\BH3_Data\Native\UserAssembly.dll"
SRC = os.path.join(HERE, "src")   # 反编译产物（旧路径 D:\Carol-start\_rea 已不存在）
CACHE = os.path.join(HERE, "addr2name.json")


def build_map():
    if os.path.exists(CACHE):
        return {int(k): v for k, v in json.load(open(CACHE, encoding="utf-8")).items()}
    pat = re.compile(
        r"//\s*([0-9A-F]{8})\s*@\s*0x([0-9A-Fa-f]+)\s*\n"
        r"\s*(?:public|private|internal|protected|static|virtual|override|sealed|new|\s)*"
        r"[^\n(]*?([A-Za-z_<>][A-Za-z0-9_<>.]*)\s*\(")
    m = {}
    for f in glob.glob(os.path.join(SRC, "*.cs")):
        t = open(f, encoding="utf-8", errors="replace").read()
        for x in pat.finditer(t):
            m.setdefault(int(x.group(2), 16), x.group(3))
    json.dump({str(k): v for k, v in m.items()}, open(CACHE, "w"), indent=0)
    return m


def read_cstr(pe, va, n=80):
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


def main():
    va = int(sys.argv[1], 0)
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    pe = PE(DLL)
    names = build_map()
    print("# 符号表 %d 条" % len(names))
    start = va
    off = pe.va2off(start)
    code = pe.data[off:off + limit * 8]
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    md.detail = True
    n = 0
    for ins in md.disasm(code, start):
        ann = ""
        if ins.mnemonic in ("call", "jmp") and ins.op_str.startswith("0x"):
            t = int(ins.op_str, 16)
            if t in names:
                ann = "   ; -> %s" % names[t]
        elif ins.mnemonic in ("call", "jmp") and ins.op_str.startswith("qword ptr [rip"):
            pass
        # RIP 相对内存操作数 → 字符串
        for op in ins.operands:
            if op.type == capstone.x86.X86_OP_MEM and op.mem.base == capstone.x86.X86_REG_RIP:
                tgt = ins.address + ins.size + op.mem.disp
                s = read_cstr(pe, tgt)
                if s:
                    ann += '   ; "%s"' % s[:50]
        print("0x%X  %-22s %-8s %-32s%s"
              % (ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str, ann))
        n += 1
        if n >= limit:
            break


if __name__ == "__main__":
    main()
