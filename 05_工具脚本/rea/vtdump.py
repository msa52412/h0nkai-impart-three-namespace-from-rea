# -*- coding: utf-8 -*-
"""vtdump —— 通用 vtable 槽位解析

用法:
    python vtdump.py <对象地址> [起始槽偏移] [结束槽偏移]
    python vtdump.py 0x700118e5a80 0x200 0x240
    python vtdump.py --vt 0x0e634340 0x200 0x240     # 直接给 vtable 地址

il2cpp 的虚表项是 16 字节 { MethodInfo*, methodPtr }，
所以真正的代码指针落在 8 mod 16 的偏移上。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402

FILE_BASE = 0x180000000
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "addr2name.json")


def q(h, va):
    b = icall.read_mem(h, va, 8)
    if not b or len(b) != 8:
        return None
    return int.from_bytes(b, "little")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    a = sys.argv[1:]
    if a[0] == "--vt":
        vt = int(a[1], 0)
        rest = a[2:]
    else:
        obj = int(a[0], 0)
        rest = a[1:]
        vt = None
    lo = int(rest[0], 0) if rest else 0x200
    hi = int(rest[1], 0) if len(rest) > 1 else lo + 0x80

    nm = {}
    if os.path.exists(CACHE):
        nm = {int(k): v for k, v in json.load(open(CACHE, encoding="utf-8")).items()}

    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        if vt is None:
            vt = q(h, obj)
            print("obj=%#x  vtable=%#x" % (obj, vt or 0))
        else:
            print("vtable=%#x" % vt)
        for off in range(lo, hi, 8):
            fn = q(h, vt + off)
            if not fn:
                continue
            if fn < base:          # MethodInfo*，跳过
                continue
            rva = fn - base
            n = nm.get(FILE_BASE + rva)
            print("  [+%#05x] %#012x  RVA %#08x  %s" % (off, fn, rva, n or "(未命名)"))
        return 0
    finally:
        icall.k32.CloseHandle(h)


if __name__ == "__main__":
    sys.exit(main() or 0)
