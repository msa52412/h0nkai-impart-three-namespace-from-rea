#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_hot_local.py —— 纯本地反汇编热点，把 callee 注解成 C# 方法名 / 导入函数名

动机：`bodies_merged.tsv` 只覆盖 C# 方法，运行时热点命中 0/6，必须现场反编译。
但"反编译"的目的其实是**看清它调了谁**。而 call 目标本身就有两张现成的名字表：

  1. `bh3_method_addr.tsv`  398,316 个 C# 方法的 rva  → VA，直接给出 Namespace.Type::Method
  2. PE 导入表              IAT 槽 → module!func，把 `call qword ptr [rip+X]` 变成实名

有了这两张表，热点函数体的调用序列就是语义指纹，不必等 Ghidra。

用法:
  python probe_hot_local.py 0x18043E4C0 ...
  python probe_hot_local.py --hot          # 读 hotspot_list.txt
  python probe_hot_local.py --all          # 读 hot6.txt
"""
import os
import struct
import sys

from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from capstone.x86 import X86_OP_IMM, X86_OP_MEM, X86_REG_RIP

from probe_thunk import PE, BASE, load_names, decode

HERE = os.path.dirname(os.path.abspath(__file__))
DLL = os.environ.get("BH3_DLL", os.path.join(HERE, "UserAssembly_slim.dll"))
METHODS = os.environ.get("BH3_METHODS", os.path.join(HERE, "bh3_method_addr.tsv"))
NAMES = os.environ.get("BH3_NAMES", os.path.join(HERE, "names_all.tsv"))

MAXINS = 900          # 单个函数最多看多少条指令
MAXBYTES = 0x1800     # 最多看多少字节


# ---------------------------------------------------------------- 名字表

def load_methods(path):
    """rva(VA) -> 'Ns.Type::Method'"""
    m = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        next(f)
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) >= 6 and p[3]:
                try:
                    m[BASE + int(p[3], 16)] = "%s::%s" % (p[4], p[5])
                except ValueError:
                    pass
    return m


def load_imports(pe):
    """IAT 槽 VA -> 'module!func'"""
    d = pe.d
    pe_off = struct.unpack_from("<I", d, 0x3C)[0]
    opt = pe_off + 24
    magic = struct.unpack_from("<H", d, opt)[0]
    dd = opt + (112 if magic == 0x20B else 96)     # data directory 起点
    n = struct.unpack_from("<I", d, dd - 4)[0]
    if n < 2:
        return {}
    imp_rva = struct.unpack_from("<I", d, dd + 8 * 1)[0]      # index 1 = Import
    if not imp_rva:
        return {}
    out = {}
    o = pe.va2off(pe.base + imp_rva)
    if o is None:
        return {}
    for _ in range(64):
        desc = d[o:o + 20]
        if len(desc) < 20 or desc == b"\x00" * 20:
            break
        oft, _ts, _fwd, name_rva, ft = struct.unpack_from("<IIIII", desc, 0)
        if not name_rva:
            break
        mod = pe.cstr(pe.base + name_rva, 64) or "?"
        src = oft or ft
        k = 0
        while k < 8192:
            eo = pe.va2off(pe.base + src + k * 8)
            if eo is None:
                break
            v = struct.unpack_from("<Q", d, eo)[0]
            if v == 0:
                break
            if v & (1 << 63):
                fn = "#%d" % (v & 0xFFFF)
            else:
                fn = pe.cstr(pe.base + v + 2, 96) if pe.va2off(
                    pe.base + v) is not None else "?"
                if not fn:
                    fn = "?"
            out[BASE + ft + k * 8] = "%s!%s" % (mod, fn)
            k += 1
        o += 20
    return out


# ---------------------------------------------------------------- 反汇编

MD = Cs(CS_ARCH_X86, CS_MODE_64)
MD.detail = True


def moff(ins, op):
    """rip 相对内存操作数的有效地址"""
    if op.mem.base != X86_REG_RIP:
        return None
    return ins.address + ins.size + op.mem.disp


def disasm_fn(pe, va, methods, imports, funames, pw):
    code = pe.bytes_at(va, MAXBYTES)
    if not code:
        pw.write("      <不可映射>\n")
        return []
    calls = []
    n = 0
    for ins in MD.disasm(code, va):
        n += 1
        if n > MAXINS:
            pw.write("      ... <截断>\n")
            break
        tag = ""
        ops = ins.operands
        if ins.mnemonic in ("call", "jmp") and ops:
            op = ops[0]
            if op.type == X86_OP_IMM:
                t = op.imm
                nm = methods.get(t) or funames.get(t)
                calls.append((ins.mnemonic, t, nm))
                tag = "   ; %s%s" % (ins.mnemonic.upper() + " ", nm or "sub_%X" % t)
            elif op.type == X86_OP_MEM:
                a = moff(ins, op)
                if a is not None and a in imports:
                    calls.append(("iat", a, imports[a]))
                    tag = "   ; %s" % imports[a]
        else:
            for op in ops:
                if op.type == X86_OP_MEM:
                    a = moff(ins, op)
                    if a is not None and a in imports:
                        tag = "   ; %s" % imports[a]
                        calls.append(("iat-ref", a, imports[a]))
                        break
                    if a is not None and ins.mnemonic in ("lea",):
                        s = pe.cstr(a, 120)
                        if s and sum(32 <= ord(c) < 127 for c in s) >= max(4, len(s) - 2):
                            tag = '   ; "%s"' % s.replace("\n", "\\n")
                            calls.append(("str", a, s))
        pw.write("      %-8X %-30s%s\n" % (ins.address, ("%s %s" % (
            ins.mnemonic, ins.op_str)).strip(), tag))
        if ins.mnemonic == "ret" and n > 6:
            nxt = pe.bytes_at(ins.address + ins.size, 4)
            if nxt and nxt[0] in (0xCC, 0x90, 0xC3):
                break
    return calls


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    if args[0] == "--hot":
        args = [ln.split()[0] for ln in
                open(os.path.join(HERE, "hotspot_list.txt"), encoding="utf-8")
                .read().splitlines() if ln.strip() and not ln.startswith("#")]
    elif args[0] == "--all":
        args = [ln.split()[0] for ln in
                open(os.path.join(HERE, "hot6.txt"), encoding="utf-8")
                .read().splitlines() if ln.strip() and not ln.startswith("#")]

    print("读二进制 ...", flush=True)
    pe = PE(DLL)
    print("读方法地址表 ...", flush=True)
    methods = load_methods(METHODS)
    print("  方法 %d" % len(methods), flush=True)
    imports = load_imports(pe)
    print("  IAT 槽 %d 个 / %d 个模块" % (
        len(imports), len({v.split("!")[0] for v in imports.values()})), flush=True)
    funames = load_names(NAMES)

    out = os.path.join(HERE, "hot_local.txt")
    with open(out, "w", encoding="utf-8") as pw:
        pw.write("binary   = %s\n" % DLL)
        pw.write("methods  = %d\n" % len(methods))
        pw.write("iat slots= %d\n\n" % len(imports))
        for a in args:
            va = int(a, 16)
            if va < BASE:
                va += BASE
            pw.write("=" * 92 + "\n")
            pw.write("VA 0x%X\n" % va)
            cur = va
            for hop in range(6):
                k, t, txt = decode(pe, cur)
                pw.write("  [hop%d] 0x%X  %-9s %s\n" % (hop, cur, k, txt))
                if k == "jmp" and t:
                    cur = t
                    continue
                break
            nmv = methods.get(cur) or funames.get(cur)
            pw.write("  -> 目标 0x%X  %s\n" % (cur, nmv or "<无名字>"))
            pw.write("  --- 反汇编 ---\n")
            calls = disasm_fn(pe, cur, methods, imports, funames, pw)

            pw.write("  --- 调用摘要 ---\n")
            seen = set()
            for kind, t, nmv in calls:
                if kind in ("call", "iat") and (kind, t) not in seen:
                    seen.add((kind, t))
                    pw.write("    %-10s 0x%-12X %s\n" % (kind, t, nmv or "sub_%X" % t))
            strs = [c for c in calls if c[0] == "str"]
            if strs:
                pw.write("  --- 字符串 ---\n")
                for _k, t, s in strs[:40]:
                    pw.write('    0x%-12X "%s"\n' % (t, s.replace("\n", "\\n")))
            pw.write("\n")
    print("done -> %s" % out)


if __name__ == "__main__":
    main()
