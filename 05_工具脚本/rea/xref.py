# -*- coding: utf-8 -*-
"""查找字符串的 RIP 相对引用（x64）。"""
import sys, struct
sys.path.insert(0, r"D:\Carol-start\_rea")
from peutil import PE


def find_xrefs(pe, target_va, extra_va=()):
    text = next(s for s in pe.sections if s["name"] == ".text")
    base_va = pe.image_base + text["va"]
    blob = pe.data[text["rptr"]:text["rptr"] + text["rsize"]]
    want = {target_va} | set(extra_va)
    out = []
    n = len(blob)
    for i in range(n - 7):
        # 48/4C 8D /r  (LEA r64, [rip+disp32])  ; 48/4C 8B /r (MOV r64)
        if blob[i] in (0x48, 0x4C) and blob[i + 1] in (0x8D, 0x8B):
            modrm = blob[i + 2]
            if (modrm & 0xC7) == 0x05:
                disp = struct.unpack_from("<i", blob, i + 3)[0]
                tgt = base_va + i + 7 + disp
                if tgt in want:
                    out.append((base_va + i, tgt, blob[i], blob[i + 1]))
    return out


if __name__ == "__main__":
    dll = r"D:\BH3\7.0\UnityPlayer.dll"
    pe = PE(dll)
    needle = b"ctable.dat"
    hits = []
    i = 0
    while True:
        i = pe.data.find(needle, i)
        if i < 0:
            break
        hits.append(i)
        i += 1
    print("ctable.dat 出现位置:", hits)
    for off in hits:
        va = pe.off2va(off)
        sec = pe.section_of_va(va)
        print("\n字符串 @file 0x%X -> VA 0x%X  节=%s" % (off, va, sec["name"] if sec else "?"))
        # 前后字符串
        seg = pe.data[max(0, off - 120):off + 160]
        strs = [s.decode("latin1") for s in __import__("re").findall(rb"[ -~]{4,80}", seg)]
        print("  邻近字符串:", strs)
        xs = find_xrefs(pe, va)
        print("  引用数:", len(xs))
        for a, t, _, _ in xs:
            print("    0x%X -> 0x%X" % (a, t))
