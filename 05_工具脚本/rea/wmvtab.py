# -*- coding: utf-8 -*-
"""wmvtab —— 把卡片实例的 vtable 槽位翻译成 C# 方法名

只读。

为什么需要
----------
DoClickAction（0x2CFB880）第一件事就是：
    mov rax,[rbx]            ; vtable
    call qword ptr [rax+0x278]
    test al,al
    jne  0x182cfbb73         ; 非零 -> 直接返回，什么都不做  ★「点击没反应」
所以必须知道 +0x278 是谁。

用法
----
    python wmvtab.py            列出 0x200~0x2A0
    python wmvtab.py 0x278      只看某个槽
"""
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402
import wmpick  # noqa: E402
import wmlock  # noqa: E402

FILE_BASE = 0x180000000
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "addr2name.json")


def names():
    if os.path.exists(CACHE):
        return {int(k): v for k, v in json.load(open(CACHE, encoding="utf-8")).items()}
    return {}


def main():
    slot = int(sys.argv[1], 0) if len(sys.argv) > 1 else None
    nm = names()
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        d = wmpick.load()
        cards = [c for c in d.get("cards", []) if c.get("feat") == 108]
        if not cards:
            print("没有 feature=108 的卡片记录")
            return 1
        card = cards[0]["this"]
        vt = wmpick.q(h, card)
        print("card=%#x  vtable=%#x  （槽位 -> RVA -> 方法名）\n" % (card, vt))
        if slot is None:
            offs = range(0x200, 0x2B0, 8)
        else:
            offs = [slot]
        for off in offs:
            fn = wmpick.q(h, vt + off)
            if not fn:
                print("  [+%#05x] = 0" % off)
                continue
            rva = fn - base
            key = FILE_BASE + rva
            n = nm.get(key)
            print("  [+%#05x] %#012x  RVA %#08x  %s"
                  % (off, fn, rva, n or "(未命名)"))
        return 0
    finally:
        icall.k32.CloseHandle(h)


if __name__ == "__main__":
    sys.exit(main() or 0)
