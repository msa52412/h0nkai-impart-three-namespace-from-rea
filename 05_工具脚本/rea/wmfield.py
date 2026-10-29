# -*- coding: utf-8 -*-
"""wmfield —— 看 feature=108 那张卡的 entry 的 +0x18 字段，以及判定函数

只读。
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402
import wmpick  # noqa: E402
import wmlock  # noqa: E402

RVA_F = 0x1F8D730     # GetWorldMapEntryStatus 里 call 的判定函数


def main():
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        d = wmpick.load()
        cd = wmlock.pick_cd(h, base, d)
        if not cd:
            return 1
        mb = st["mailbox"]
        lst = wmpick.call(h, base, mb, wmpick.RVA_GET_ENTRIES, cd)
        items, n = wmpick.list_items(h, lst)
        e = wmpick.q(h, items + 0x20)
        print("\nentry = %#x" % e)
        print("  +0x00 vtable      = %#x" % (wmpick.q(h, e) or 0))
        print("  +0x08             = %#x" % (wmpick.q(h, e + 0x08) or 0))
        print("  +0x10 type        = %s" % wmpick.i32(h, e + 0x10))
        print("  +0x14 contentID   = %s" % wmpick.i32(h, e + 0x14))
        p18 = wmpick.q(h, e + 0x18)
        print("  +0x18             = %#x   %s" % (p18 or 0, "NULL ← 直接判 2" if not p18 else ""))
        if p18:
            print("        [+0x00] vtable = %#x" % (wmpick.q(h, p18) or 0))
            for off in range(0x08, 0x40, 8):
                v = wmpick.q(h, p18 + off)
                print("        [+%#04x] = %#x  (%s)" % (off, v or 0, wmpick.i32(h, p18 + off)))
        # 直接现场调判定函数，看它返回什么
        r = wmpick.call(h, base, mb, RVA_F, p18) if p18 else None
        print("\n  f([entry+0x18]) = %s" % r)
        print()
        wmlock.disas(base, RVA_F, 0x80, "entry 状态判定函数 f")
        return 0
    finally:
        icall.k32.CloseHandle(h)


if __name__ == "__main__":
    sys.exit(main() or 0)
