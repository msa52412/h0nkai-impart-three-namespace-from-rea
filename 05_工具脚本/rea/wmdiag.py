# -*- coding: utf-8 -*-
"""wmdiag —— 只读诊断：把三个页签里每张卡的 identity 三元组打出来

要回答的问题
------------
`wmpick.py setup --yes` 最后一步报「找不到 feature=108 的卡片」，
但同一函数在开头明明找到了 109。怀疑点：
  A) 写入 ftl+0x20 后，JONKHNOFPPH(cd) 读的不是同一处（走了转换/缓存）
  B) meta 指针身份在写入后变了（重建了 ExcelMeta）
  C) 卡片列表本身在刷新后换了对象

本脚本对每张卡同时打印：
  cd / meta / [cd+0x18] / JONKHNOFPPH(cd) / meta+0x10 / meta+0x20 / [meta+0x18]+0x20
三个数据源放在一起，谁和谁一致一眼就能看出来。

用法：python wmdiag.py
安全：全只读，不写任何内存。
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
            print("信箱未装/失效，先跑 python wmpick.py arm")
            return 1
        mb = st["mailbox"]

        d = W.load() or {}
        mgr = d.get("mgr") if d.get("pid") == pid else None
        if not mgr:
            raw = icall.read_mem(h, st["page"] + W.MGR_SLOT, 8)
            mgr = struct.unpack("<Q", raw)[0] if raw and len(raw) == 8 else 0
        print("pid=%d base=%#x mailbox=%#x" % (pid, base, mb))
        print("MonoWorldMapUIManager = %#x" % mgr)
        if not mgr:
            print("✗ 管理器实例没抓到 —— 游戏里关掉挑战面板再打开一次，然后重跑")
            return 1

        for off, name in W.TAB_FIELDS:
            lst = W.q(h, mgr + off)
            print("\n=== %s  (mgr+%#x = %#x)" % (name, off, lst))
            if not lst:
                print("   空")
                continue
            items, n = W.list_items(h, lst)
            if not items:
                print("   列表读不出来")
                continue
            print("   items=%#x n=%d" % (items, n))
            for i in range(min(n, 24)):
                c = W.q(h, items + 0x20 + i * 8)
                if not c:
                    print("   [%2d] <null>" % i)
                    continue
                cd = W.q(h, c + W.OFF_CONTAINER)
                if not cd:
                    print("   [%2d] card=%#x  ContainerData=<null>" % (i, c))
                    continue
                f = W.call(h, base, mb, W.RVA_GET_FEATURE, cd)
                meta = W.call(h, base, mb, W.RVA_GET_META, cd)
                meta_f = W.q(h, cd + 0x18)
                ftl = W.q(h, meta + 0x18) if meta else 0
                ft0 = W.i32(h, ftl + 0x20) if ftl else None
                print("   [%2d] card=%#x cd=%#x meta=%#x [cd+0x18]=%#x feat=%s "
                      "ID=%s ftl=%#x ft[0]=%s"
                      % (i, c, cd, meta, meta_f, f,
                         W.i32(h, meta + 0x20) if meta else "?",
                         ftl, ft0))
        return 0
    finally:
        icall.k32.CloseHandle(h)


if __name__ == "__main__":
    sys.exit(main())
