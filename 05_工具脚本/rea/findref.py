# -*- coding: utf-8 -*-
"""扫描对指定 VA 的 RIP 相对引用（读/写都算），覆盖常见 mov/lea 编码。"""
import sys, struct
sys.path.insert(0, r"D:\Carol-start\_rea")
from peutil import PE

DLL = r"D:\BH3\7.0\UnityPlayer.dll"

# 常见形式：REX 48/4C [8B/89/8D/C7] modrm(rip) disp32
PAT_RIP = []
for rex in (0x48, 0x4C, 0x49, 0x4D):
    for op in (0x8B, 0x89, 0x8D, 0xC7, 0x3B, 0x39, 0x03, 0x01):
        PAT_RIP.append((rex, op))


def scan(target_va, pe=None, limit=40):
    pe = pe or PE(DLL)
    text = next(s for s in pe.sections if s["name"] == ".text")
    base = pe.image_base + text["va"]
    blob = pe.data[text["rptr"]:text["rptr"] + text["rsize"]]
    out = []
    n = len(blob)
    for i in range(n - 7):
        r, o = blob[i], blob[i + 1]
        if (r, o) not in PAT_RIP:
            continue
        if (blob[i + 2] & 0xC7) != 0x05:
            continue
        disp = struct.unpack_from("<i", blob, i + 3)[0]
        if base + i + 7 + disp == target_va:
            out.append((base + i, o))
            if len(out) >= limit:
                break
    return out


if __name__ == "__main__":
    tgt = int(sys.argv[1], 16)
    pe = PE(DLL)
    res = scan(tgt, pe)
    print("目标 0x%X 的引用 %d 处" % (tgt, len(res)))
    for va, op in res:
        kind = {0x8B: "读", 0x89: "写", 0x8D: "lea", 0xC7: "写立即数",
                0x3B: "cmp", 0x39: "cmp", 0x03: "读", 0x01: "写"}.get(op, "?")
        print("  0x%X  %s" % (va, kind))
