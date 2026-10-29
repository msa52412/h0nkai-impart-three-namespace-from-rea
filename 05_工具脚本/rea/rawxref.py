#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rawxref.py —— 原始字节级 rip 相对 xref 扫描（不依赖函数边界，可覆盖整节）。

用法：python rawxref.py 0x1899DBBE8 [--sec il2cpp|text|both]
"""
import struct
import sys

PATH = r"Z:\AI\7.0\BH3_Data\Native\UserAssembly.dll"
IB = 0x180000000
d = open(PATH, "rb").read()

e = struct.unpack_from("<I", d, 0x3C)[0]
coff = e + 4
nsec = struct.unpack_from("<H", d, coff + 2)[0]
optsz = struct.unpack_from("<H", d, coff + 16)[0]
SECS = {}
for i in range(nsec):
    o = coff + 20 + optsz + i * 40
    nm = d[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    key = nm.lstrip(".")
    if key not in SECS:
        SECS[key] = (va, vs, rs, rp)

# 需要识别的 rip 相对取址指令（ModR/M 的 mod=00, rm=101）
# 48 8B /r  mov r64,[rip+d]   ; 48 8D /r lea  ; 8B /r mov r32  ; 48 89 /r mov [rip+d],r
PATTERNS = [b"\x48\x8b", b"\x48\x8d", b"\x8b", b"\x48\x89", b"\x89", b"\x4c\x8b", b"\x48\xc7"]
RM = (0x05, 0x0D, 0x15, 0x1D, 0x25, 0x2D, 0x35, 0x3D)


def scan(secname, targets, want_write):
    va, vs, rs, rp = SECS[secname]
    blob = d[rp:rp + rs]
    lo = IB + va
    hits = []
    n = len(blob)
    i = 0
    # 逐个字节尝试两种前缀长度（1 或 2）
    for i in range(n - 7):
        b0 = blob[i]
        for plen in (1, 2):
            if plen == 2:
                if b0 < 0x40 or b0 > 0x4F:
                    continue
                if i + 1 >= n:
                    continue
                op = blob[i + 1]
                if op not in (0x8B, 0x8D, 0x89, 0xC7):
                    continue
            else:
                op = b0
                if op not in (0x8B, 0x8D, 0x89, 0xC7):
                    continue
            m = blob[i + plen]
            if m not in RM:
                continue
            addr = lo + i
            disp = struct.unpack_from("<i", blob, i + plen + 1)[0]
            t = addr + plen + 5 + disp
            if t in targets:
                isw = (op == 0x89)
                if want_write is not None and isw != want_write:
                    continue
                hits.append((addr, secname, isw, blob[i:i + plen + 5].hex()))
    return hits


def main():
    targets = set()
    for a in sys.argv[1:]:
        if a.startswith("0x"):
            targets.add(int(a, 16))
    secs = ["text", "il2cpp"] if "--sec" not in sys.argv else [sys.argv[sys.argv.index("--sec") + 1]]
    want_write = None
    if "--write" in sys.argv:
        want_write = True
    if "--read" in sys.argv:
        want_write = False
    for s in secs:
        if s not in SECS:
            print("无此节 %s" % s)
            continue
        hits = scan(s, targets, want_write)
        print("== 节 %s: 命中 %d 处" % (s, len(hits)))
        for addr, sec, isw, hx in hits[:40]:
            print("   0x%X  %s  %s  %s" % (addr, sec, "写" if isw else "读", hx))


if __name__ == "__main__":
    main()
