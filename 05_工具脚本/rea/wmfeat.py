# -*- coding: utf-8 -*-
"""wmfeat —— 搞清 OODENFBANCC.JONKHNOFPPH (feature getter) 到底读哪块内存

背景
----
`wmpick.py setup` 把 `[meta+0x18]+0x20` 写成 108，回读确认是 108，
但 `JONKHNOFPPH(cd)` 仍返回 109。所以 getter 读的不是那里。

两种可能
--------
  1. 读 entry 列表：FNPIAMHFCKC +0x10 (GeneralActivityType)
  2. 读 ExcelMeta 另一条链：HHCFLLHHHKB(meta) 里做了转换/取缓存

子命令
------
  python wmfeat.py            反汇编 JONKHNOFPPH + HHCFLLHHHKB（离线，不碰游戏）
  python wmfeat.py live       对目标卡片现场 dump：entries 每项的 +0x10/+0x14
                             以及各条链的指针值（只读）
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402
import wmpick as W  # noqa: E402
from capstone import Cs, CS_ARCH_X86, CS_MODE_64  # noqa: E402

FILE_BASE = 0x180000000

TARGETS = [
    (0xA51E70, "OODENFBANCC.JONKHNOFPPH   (feature getter)"),
    (0x44FBF90, "ExcelMeta.HHCFLLHHHKB"),
    (0xA51730, "OODENFBANCC.ACEGIOFPCNN   (entries getter)"),
]


def disasm(rva, title, n=180):
    print("\n=== %s  @RVA %#x" % (title, rva))
    raw = icall.file_bytes(rva, n)
    if not raw:
        print("  读不到文件字节")
        return
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True
    count = 0
    for ins in md.disasm(raw, FILE_BASE + rva):
        print("  %#x  %-22s %-8s %s"
              % (ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str))
        count += 1
        # 遇到 ret 且已经走过几条就停（避免串到下一个函数）
        if ins.mnemonic == "ret" and count > 4:
            break
        if ins.mnemonic == "int3":
            break
        if count > 120:
            break


def cmd_offline():
    for rva, title in TARGETS:
        disasm(rva, title)
    return 0


def cmd_live():
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        if not st or st.get("pid") != pid:
            print("信箱未装/失效，先跑 python wmpick.py arm")
            return 1
        mb = st["mailbox"]
        d = W.load() or {}
        mgr = d.get("mgr") if d.get("pid") == pid else None
        if not mgr:
            raw = icall.read_mem(h, st["page"] + W.MGR_SLOT, 8)
            mgr = struct.unpack("<Q", raw)[0] if raw and len(raw) == 8 else 0
        if not mgr:
            print("✗ 管理器实例没抓到，先关开一次挑战面板")
            return 1

        # 找 feature=109 的那张（悬赏委托）
        target = None
        for off, name in W.TAB_FIELDS:
            lst = W.q(h, mgr + off)
            if not lst:
                continue
            items, n = W.list_items(h, lst)
            if not items:
                continue
            for i in range(min(n, 24)):
                c = W.q(h, items + 0x20 + i * 8)
                cd = W.q(h, c + W.OFF_CONTAINER) if c else 0
                if not cd:
                    continue
                f = W.call(h, base, mb, W.RVA_GET_FEATURE, cd)
                if f in (W.OLD_FEATURE, W.NEW_FEATURE):
                    target = (name, i, c, cd)
                    break
            if target:
                break
        if not target:
            print("✗ 没找到 feature 109/108 的卡")
            return 1
        tab, idx, c, cd = target
        print("%s [%d] card=%#x cd=%#x" % (tab, idx, c, cd))

        meta = W.call(h, base, mb, W.RVA_GET_META, cd)
        print("\nRVA_GET_META(cd)          = %#x" % meta)
        print("q(cd+0x18)                = %#x" % W.q(h, cd + 0x18))
        print("RVA_GET_FEATURE(cd)       = %s" % W.call(h, base, mb, W.RVA_GET_FEATURE, cd))
        print("RVA_GET_FT(meta)          = %#x" % (W.call(h, base, mb, W.RVA_GET_FT, meta) or 0))
        print("q(meta+0x18)              = %#x" % W.q(h, meta + 0x18))
        print("q(meta+0x10)              = %#x" % W.q(h, meta + 0x10))

        # entries 链
        el = W.call(h, base, mb, W.RVA_GET_ENTRIES, cd)
        print("\nRVA_GET_ENTRIES(cd)       = %#x" % (el or 0))
        if el:
            items, n = W.list_items(h, el)
            print("  items=%#x n=%d" % (items or 0, n))
            for i in range(min(n, 8)):
                e = W.q(h, items + 0x20 + i * 8)
                if not e:
                    print("  [%d] <null>" % i)
                    continue
                print("  [%d] entry=%#x  +0x10=%s  +0x14=%s  +0x18=%#x"
                      % (i, e, W.i32(h, e + 0x10), W.i32(h, e + 0x14),
                         W.q(h, e + 0x18)))

        # showType / content
        print("\nRVA_GET_SHOWTYPE(cd)      = %s"
              % W.call(h, base, mb, W.RVA_GET_SHOWTYPE, cd))
        return 0
    finally:
        icall.k32.CloseHandle(h)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "live":
        return cmd_live()
    return cmd_offline()


if __name__ == "__main__":
    sys.exit(main())
