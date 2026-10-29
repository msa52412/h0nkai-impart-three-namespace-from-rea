# -*- coding: utf-8 -*-
"""定位 UnityPlayer.dll 中 GenerateHash 相关字符串的引用代码"""
import sys, struct
import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

P = r"D:\BH3\7.0\UnityPlayer.dll"
pe = pefile.PE(P, fast_load=False)
ib = pe.OPTIONAL_HEADER.ImageBase
d = open(P, "rb").read()
secs = [(s.Name.rstrip(b"\0").decode(), ib + s.VirtualAddress, s.Misc_VirtualSize,
         s.PointerToRawData, s.SizeOfRawData) for s in pe.sections]

def off2va(off):
    for n, base, vsz, praw, rsz in secs:
        if praw <= off < praw + rsz:
            return base + (off - praw)
    return None

def va2off(va):
    for n, base, vsz, praw, rsz in secs:
        if base <= va < base + max(vsz, rsz):
            return praw + (va - base)
    return None

text = [s for s in secs if s[0] == ".text"][0]
tbase, tvsz, tpr, trs = text[1], text[2], text[3], text[4]
code = d[tpr:tpr + trs]

# 收集字符串
strs = {}
for kw in [b"GenerateHash", b"Failed to load il2cpp", b"Native/UserAssembly.dll",
           b"Failed to initialize IL2CPP"]:
    i = 0
    while True:
        i = d.find(kw, i)
        if i < 0: break
        va = off2va(i)
        if va: strs.setdefault(kw.decode(), []).append(va)
        i += 1
for k, v in strs.items():
    print("%-32s %s" % (k, [hex(x) for x in v]))

allva = {va: k for k, vs in strs.items() for va in vs}
print("\n在 .text 中查找 lea 引用（指向字符串起点 ±0x40 内）:")
md = Cs(CS_ARCH_X86, CS_MODE_64)
found = {}
for i in range(len(code) - 7):
    if code[i] in (0x48, 0x4C) and code[i+1] == 0x8D and (code[i+2] & 0xC7) == 0x05:
        disp = struct.unpack_from("<i", code, i+3)[0]
        t = tbase + i + 7 + disp
        for sva, name in allva.items():
            if sva - 0x80 <= t <= sva + 0x80:
                found.setdefault(name, []).append((tbase + i, t))
for name, lst in found.items():
    print("  %s -> %d 处" % (name, len(lst)))
    for a, t in lst[:6]:
        print("     %#x  -> %#x" % (a, t))
