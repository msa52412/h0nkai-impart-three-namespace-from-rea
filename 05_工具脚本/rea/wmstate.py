# -*- coding: utf-8 -*-
"""wmstate —— 一键看点击接线状态（只读）

看三件事：
  1) DoClickAction 入口指向哪个 stub
  2) 信箱里的 target 是哪条命令（GoToOWEndless 说明 stub 触发过；get_Group 说明还是旧的）
  3) 捕获槽里最后被点的是哪张卡
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402
import wmpick  # noqa: E402

KNOWN = {
    0x1A92080: "MonoWorldMapEndlessEntry.get_module",
    0x189DC90: "OWEndlessModule.get_Group",
    0x19C5E00: "OWEndlessModule.GoToOWEndless  ★我们的命令",
}


def main():
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        if not st or st.get("pid") != pid:
            print("信箱未装/失效")
            return 1
        page, mb = st["page"], st["mailbox"]

        cur = icall.read_mem(h, base + wmpick.RVA_DOCLICK, 14)
        if cur and cur[:2] == b"\xFF\x25":
            tgt = struct.unpack("<Q", cur[6:])[0]
            which = "click stub" if tgt == page + wmpick.CLICK_STUB_OFF else (
                "capture stub" if tgt == page + wmpick.CAPTURE_STUB else "未知")
            print("DoClickAction 入口 → %#x  (%s)" % (tgt, which))
        else:
            print("DoClickAction 入口 = %s（未挂钩）" % (cur.hex(" ") if cur else "?"))

        raw = icall.read_mem(h, mb, 0x40)
        pend, done = raw[0], raw[1]
        tgt = struct.unpack("<Q", raw[8:16])[0]
        arg0 = struct.unpack("<Q", raw[16:24])[0]
        name = KNOWN.get(tgt - base, None)
        print("信箱 pending=%#04x done=%d" % (pend, done))
        print("     target = %#x  RVA %#x  %s" % (tgt, tgt - base, name or "(不在已知表里)"))
        print("     arg0   = %#x" % arg0)

        slot = icall.read_mem(h, page + wmpick.SLOT, 8)
        v = struct.unpack("<Q", slot)[0] if slot and len(slot) == 8 else 0
        print("捕获槽（最后点击的卡片）= %#x" % v)
        if v:
            cd = wmpick.q(h, v + 0xC8)
            print("     ContainerData = %#x" % (cd or 0))
            if cd:
                meta = wmpick.q(h, cd + 0x18)
                ft = wmpick.q(h, meta + 0x18) if meta else None
                if ft:
                    n = wmpick.i32(h, ft + 0x18)
                    vals = [wmpick.i32(h, ft + 0x20 + i * 4) for i in range(min(n or 0, 6))]
                    print("     meta=%#x  FeatureType 长度=%s 值=%s" % (meta, n, vals))
        return 0
    finally:
        icall.k32.CloseHandle(h)


if __name__ == "__main__":
    sys.exit(main() or 0)
