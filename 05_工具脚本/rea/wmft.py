# -*- coding: utf-8 -*-
"""wmft —— 摸清 FeatureType 的真实内存布局（只读）

为什么需要
----------
stub 里的判断链是  cd+0x18 -> +0x18 -> [+0x20]==108。
JONKHNOFPPH(0xA51E70) 实际走的是 HHCFLLHHHKB(0x44FBF90)，而它不是简单取字段：
    call MPGEDEILLAD()
    rcx = [meta+0x18]
    edx = 0 ; r8d = 4
    jmp AAGPFOHOKJL(rcx, 0, 4)      ; 可能是 List<int> -> int[] 的转换
所以 [meta+0x18] 可能是 List<int> 而不是 int[]，两种布局差一个间接层。
这个脚本把两种解释都打出来，用实测数据判定。
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402
import wmpick  # noqa: E402
import wmlock  # noqa: E402


def dump(h, va, n=0x40, tag=""):
    b = icall.read_mem(h, va, n)
    if not b:
        print("  %s%#x 读取失败" % (tag, va))
        return
    print("  %s%#x" % (tag, va))
    for i in range(0, len(b), 16):
        print("    +%02x  %s" % (i, b[i:i + 16].hex(" ")))


def main():
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        d = wmpick.load()
        print("pid=%d base=%#x  page=%#x mailbox=%#x"
              % (pid, base, st["page"], st["mailbox"]))
        dump(h, st["mailbox"], 0x40, "信箱 ")

        cd = wmlock.pick_cd(h, base, d)
        if not cd:
            return 1
        meta = wmpick.q(h, cd + 0x18)
        print("\ncd=%#x  cd+0x18(meta)=%#x" % (cd, meta or 0))
        dump(h, meta, 0x40, "meta ")
        ft = wmpick.q(h, meta + 0x18)
        print("\nmeta+0x18 = %#x" % (ft or 0))
        dump(h, ft, 0x40, "obj  ")

        print("\n--- 两种解释 ---")
        print("  当作 int[] : 长度[+0x18]=%s  元素[+0x20..]=%s"
              % (wmpick.i32(h, ft + 0x18),
                 [wmpick.i32(h, ft + 0x20 + i * 4) for i in range(4)]))
        items = wmpick.q(h, ft + 0x10)
        print("  当作 List<int>: _items[+0x10]=%#x  _size[+0x18]=%s"
              % (items or 0, wmpick.i32(h, ft + 0x18)))
        if items:
            dump(h, items, 0x30, "  _items ")
            print("     int[] 长度[+0x18]=%s  元素[+0x20..]=%s"
                  % (wmpick.i32(h, items + 0x18),
                     [wmpick.i32(h, items + 0x20 + i * 4) for i in range(4)]))

        print("\n--- 对照 getter 实际返回 ---")
        print("  JONKHNOFPPH(cd) = %s" % wmpick.call(h, base, st["mailbox"],
                                                    wmpick.RVA_GET_FEATURE, cd))
        return 0
    finally:
        icall.k32.CloseHandle(h)


if __name__ == "__main__":
    sys.exit(main() or 0)
