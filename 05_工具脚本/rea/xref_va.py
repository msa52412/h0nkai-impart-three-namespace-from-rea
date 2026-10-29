# -*- coding: utf-8 -*-
"""找指定 VA 的调用者，并反汇编上下文"""
import sys, struct
import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

P = r"D:\BH3\7.0\UnityPlayer.dll"
pe = pefile.PE(P, fast_load=False)
ib = pe.OPTIONAL_HEADER.ImageBase
d = open(P, "rb").read()

secs = [(s.Name.rstrip(b"\0").decode(), ib + s.VirtualAddress, s.Misc_VirtualSize,
         s.PointerToRawData, s.SizeOfRawData) for s in pe.sections]

def va2off(va):
    for n, base, vsz, praw, rsz in secs:
        if base <= va < base + max(vsz, rsz):
            return praw + (va - base)
    return None

def sec_of(va):
    for n, base, vsz, praw, rsz in secs:
        if base <= va < base + max(vsz, rsz):
            return n
    return None

text = [s for s in secs if s[0] == ".text"][0]
tname, tbase, tvsz, tpr, trs = text
code = d[tpr:tpr + trs]

def callers(target, limit=40):
    out = []
    for i in range(len(code) - 5):
        if code[i] == 0xE8:
            rel = struct.unpack_from("<i", code, i + 1)[0]
            if tbase + i + 5 + rel == target:
                out.append(tbase + i)
        elif code[i] == 0xE9:
            rel = struct.unpack_from("<i", code, i + 1)[0]
            if tbase + i + 5 + rel == target:
                out.append(tbase + i)
        if len(out) >= limit:
            break
    return out

md = Cs(CS_ARCH_X86, CS_MODE_64)

def dump(va, before=0x60, after=0x60, title=""):
    o = va2off(va - before)
    if o is None:
        print("  [%s] 无法映射 %#x" % (title, va)); return
    blob = d[o:o + before + after]
    print("\n--- %s @ %#x (%s) ---" % (title, va, sec_of(va)))
    for insn in md.disasm(blob, va - before):
        mark = "   <<<" if insn.address == va else ""
        print("  %#010x  %-8s %-44s%s" % (insn.address, insn.mnemonic, insn.op_str, mark))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        targets = [int(sys.argv[1], 0)]
    else:
        targets = [0x18133fbda, 0x180e2d8f5]
    for t in targets:
        cs = callers(t)
        print("\n===== 目标 %#x  调用者 %d 个 =====" % (t, len(cs)))
        for c in cs[:8]:
            print("   %#x" % c)
        for c in cs[:2]:
            dump(c, 0x50, 0x60, "call-site")
