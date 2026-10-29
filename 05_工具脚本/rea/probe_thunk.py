#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_thunk.py —— 纯本地解析 jump/call thunk，不需要 Ghidra

§9O 的经验：`0x1804FE000` 这一片是 MSVC 增量链接的桩表，每个桩要么是
5 字节 `E9 rel32`（JMP），要么是 `E8 rel32 + CC`（CALL + INT3）。语义全在目标里。
既然二进制在本地，这一步就不该占用远端 Ghidra。

用法:
  python probe_thunk.py 0x18043E4C0 0x1803EE250 ...
  python probe_thunk.py --hot        读 hotspot_list.txt
"""
import struct
import sys
import os

DLL = os.environ.get("BH3_DLL", "UserAssembly_slim.dll")
NAMES = os.environ.get("BH3_NAMES", "names_all.tsv")

BASE = 0x180000000


class PE:
    def __init__(self, path):
        self.d = open(path, "rb").read()
        d = self.d
        pe = struct.unpack_from("<I", d, 0x3C)[0]
        nsec = struct.unpack_from("<H", d, pe + 6)[0]
        opt = pe + 24
        self.base = struct.unpack_from("<Q", d, opt + 24)[0]
        self.nsec = nsec
        so = opt + struct.unpack_from("<H", d, pe + 20)[0]
        self.secs = []
        for i in range(nsec):
            o = so + i * 40
            nm = d[o:o + 8].rstrip(b"\x00").decode(errors="replace")
            vs, va, rs, ra = struct.unpack_from("<IIII", d, o + 8)
            self.secs.append((nm, va, vs, ra, rs))

    def va2off(self, va):
        rva = va - self.base
        for nm, vaddr, vsize, raw, rsize in self.secs:
            if vaddr <= rva < vaddr + max(vsize, rsize):
                if raw == 0:
                    return None
                off = raw + (rva - vaddr)
                if off + 1 <= len(self.d):
                    return off
        return None

    def bytes_at(self, va, n=16):
        o = self.va2off(va)
        if o is None:
            return None
        return self.d[o:o + n]

    def cstr(self, va, limit=64):
        o = self.va2off(va)
        if o is None:
            return None
        e = self.d.find(b"\x00", o, o + limit)
        if e < 0:
            e = o + limit
        try:
            return self.d[o:e].decode("utf-8")
        except UnicodeDecodeError:
            return None


def load_names(path):
    m = {}
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            next(f)
            for ln in f:
                p = ln.rstrip("\n").split("\t")
                if len(p) >= 2:
                    try:
                        m[int(p[0], 16)] = p[1]
                    except ValueError:
                        pass
    except FileNotFoundError:
        pass
    return m


NAMEMAP = load_names(NAMES)


def nm(va):
    if va in NAMEMAP:
        return NAMEMAP[va]
    return "?"


def decode(pe, va):
    """返回 (kind, target, text) —— kind in {jmp, call, call_int3, other}"""
    b = pe.bytes_at(va, 16)
    if not b:
        return "unmapped", None, "<不可映射>"
    hexs = " ".join("%02X" % x for x in b[:12])
    if b[0] == 0xE9:
        rel = struct.unpack_from("<i", b, 1)[0]
        t = va + 5 + rel
        return "jmp", t, "E9 -> 0x%X (%s)" % (t, nm(t))
    if b[0] == 0xE8:
        rel = struct.unpack_from("<i", b, 1)[0]
        t = va + 5 + rel
        kind = "call_int3" if len(b) > 5 and b[5] == 0xCC else "call"
        return kind, t, "E8 -> 0x%X (%s)%s" % (
            t, nm(t), " + INT3" if kind == "call_int3" else "")
    if b[0] == 0xCC:
        return "other", None, "CC（空桩/对齐）"
    return "other", None, hexs


def trace(pe, va, maxhop=6):
    print("=" * 78)
    print("0x%X   %s" % (va, nm(va)))
    cur = va
    seen = set()
    for hop in range(maxhop):
        if cur in seen:
            print("   ↻ 环")
            break
        seen.add(cur)
        k, t, txt = decode(pe, cur)
        print("   [%d] 0x%X  %-9s %s" % (hop, cur, k, txt))
        if k in ("jmp",) and t:
            cur = t
            continue
        break
    return cur


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    if args[0] == "--hot":
        args = [ln.split()[0] for ln in
                open("hotspot_list.txt", encoding="utf-8").read().splitlines()
                if ln.strip() and not ln.startswith("#")]
    pe = PE(DLL)
    for a in args:
        va = int(a, 16) if not a.lower().startswith("0x") else int(a, 16)
        if va < BASE:
            va += BASE
        trace(pe, va)
    print()


if __name__ == "__main__":
    main()
