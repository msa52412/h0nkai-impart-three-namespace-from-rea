# -*- coding: utf-8 -*-
"""用 .pdata 找包含指定 VA 的函数边界，并查该函数的调用者"""
import sys, struct
import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

P = r"D:\BH3\7.0\UnityPlayer.dll"
pe = pefile.PE(P, fast_load=False)
ib = pe.OPTIONAL_HEADER.ImageBase
d = open(P, "rb").read()
secs = [(s.Name.rstrip(b"\0").decode(), ib + s.VirtualAddress, s.Misc_VirtualSize,
         s.PointerToRawData, s.SizeOfRawData) for s in pe.sections]
text = [s for s in secs if s[0] == ".text"][0]
tbase, tvsz, tpr, trs = text[1], text[2], text[3], text[4]
code = d[tpr:tpr + trs]

funcs = []
for e in pe.DIRECTORY_ENTRY_EXCEPTION:
    funcs.append((e.struct.BeginAddress + ib, e.struct.EndAddress + ib))
funcs.sort()
print("函数条目:", len(funcs))

def containing(va):
    lo, hi = 0, len(funcs) - 1
    best = None
    while lo <= hi:
        mid = (lo + hi) // 2
        b, e = funcs[mid]
        if b <= va < e:
            return (b, e)
        if va < b:
            hi = mid - 1
        else:
            lo = mid + 1
    return best

def va2off(va):
    for n, base, vsz, praw, rsz in secs:
        if base <= va < base + max(vsz, rsz):
            return praw + (va - base)
    return None

def callers(target, limit=30):
    out = []
    for i in range(len(code) - 5):
        op = code[i]
        if op in (0xE8, 0xE9):
            rel = struct.unpack_from("<i", code, i + 1)[0]
            if tbase + i + 5 + rel == target:
                out.append((tbase + i, "call" if op == 0xE8 else "jmp"))
                if len(out) >= limit:
                    break
    return out

md = Cs(CS_ARCH_X86, CS_MODE_64)

def dump(va, n=0x80):
    o = va2off(va)
    if o is None:
        print("  无法映射"); return
    for insn in md.disasm(d[o:o+n], va):
        print("    %#010x  %-8s %-42s" % (insn.address, insn.mnemonic, insn.op_str))

for t in [int(x, 0) for x in sys.argv[1:]] or [0x181326900, 0x18097e060]:
    r = containing(t)
    print("\n===== %#x 所属函数: %s =====" % (t, ("%#x..%#x" % r) if r else "未知(pdata 无记录)"))
    if r:
        print("  函数长度: %#x" % (r[1] - r[0]))
        cs = callers(r[0])
        print("  调用者 %d 个:" % len(cs))
        for a, k in cs[:12]:
            cr = containing(a)
            print("     %#x %-4s  在函数 %s" % (a, k, ("%#x..%#x" % cr) if cr else "?"))
        print("  函数入口反汇编:")
        dump(r[0], 0x50)
