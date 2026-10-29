# -*- coding: utf-8 -*-
"""wmverify —— 现场确认点击接线真的落到内存了（只读）

检查三件事：
  1. DoClickAction 入口前 16 字节是不是 48 B8 <stub> FF E0（movabs rax,stub; jmp rax）
  2. stub 区（page+0x6000）头几个字节是否是预期机器码
  3. 信箱头 / 捕获槽 / 管理器槽 三个指针是否都非 0

用法：python wmverify.py
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402
import wmpick as W  # noqa: E402


def main():
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        if not st or st.get("pid") != pid:
            print("✗ 信箱未装/失效，先跑 python wmpick.py arm")
            return 1
        page, mb = st["page"], st["mailbox"]

        entry = base + W.RVA_DOCLICK
        raw = icall.read_mem(h, entry, 16)
        print("DoClickAction 入口 %#x" % entry)
        print("  前16字节 = %s" % (raw.hex(" ") if raw else "读不到"))
        # 实际用的跳板是 14 字节绝对间接跳：
        #   ff 25 00 00 00 00      jmp qword ptr [rip+0]
        #   <8 字节绝对地址>       被跳转目标
        ok = False
        if raw and len(raw) >= 14 and raw[:6] == bytes.fromhex("ff2500000000"):
            tgt = struct.unpack_from("<Q", raw, 6)[0]
            print("  → jmp qword [rip+0] → %#x" % tgt)
            print("  → 与 page+0x6000 (%#x) %s" % (page + W.CLICK_STUB_OFF,
                                                   "一致 ✓" if tgt == page + W.CLICK_STUB_OFF else "不一致 ✗"))
            ok = tgt == page + W.CLICK_STUB_OFF
        elif raw and len(raw) >= 12 and raw[0] == 0x48 and raw[1] == 0xB8 and raw[10] == 0xFF and raw[11] == 0xE0:
            tgt = struct.unpack_from("<Q", raw, 2)[0]
            print("  → movabs rax, %#x ; jmp rax" % tgt)
            print("  → 与 page+0x6000 (%#x) %s" % (page + W.CLICK_STUB_OFF,
                                                   "一致 ✓" if tgt == page + W.CLICK_STUB_OFF else "不一致 ✗"))
            ok = tgt == page + W.CLICK_STUB_OFF
        else:
            print("  → 不是预期跳板（钩子没装上，或原始 prologue）")

        stub = icall.read_mem(h, page + W.CLICK_STUB_OFF, 32)
        print("\nstub @ %#x" % (page + W.CLICK_STUB_OFF))
        print("  前32字节 = %s" % (stub.hex(" ") if stub else "读不到"))

        print("\n信箱区")
        for name, off in (("信箱头", 0), ("捕获槽", 0x40), ("管理器槽", 0x48)):
            v = icall.read_mem(h, page + off, 8)
            print("  %-6s +%#04x = %#x" % (name, off, struct.unpack("<Q", v)[0] if v and len(v) == 8 else 0))

        print("\n结论：%s" % ("接线在内存里，可以点卡" if ok else "接线不在，需要重跑 wmready --force"))
        return 0 if ok else 1
    finally:
        icall.k32.CloseHandle(h)


if __name__ == "__main__":
    sys.exit(main())
