# -*- coding: utf-8 -*-
"""groupprobe.py — 复现 RefreshPlayerGroup 用的那条查表链，逐档验证是否会 NRE。

为什么不能只信 get_GroupName
---------------------------
get_GroupName(0xEF9320) 的链是：
    meta = GetOWEndlessGroupMetaByKey(this+0x24)
    hash = NGODNLMBIEL.OAJJFLJIBNL(meta)
    name = TextMap...(hash)

而 RefreshPlayerGroup(0x1859850) 的链是：
    meta = GetOWEndlessGroupMetaByKey(data+0x24)
    test rax,rax  -> je 0x1859c4f        <-- 空则异常（黑屏）
    hash = NGODNLMBIEL.BNCMBEGMMAN(meta) <-- 注意：另一个 getter
    name = BMKMGBALPKO.EJDCEEKDDGL(hash, activeMode)
    test rax,rax  -> je 0x1859b9a        <-- 空则异常
0x1859850+0x404 = 0x1859C54 正好落在这段异常链上。

本脚本按 RefreshPlayerGroup 的顺序原样调一遍，打印每一步是否为空。

2026-10-25 21:1x 崩溃事故
------------------------
第一版把 RVA 写成了反汇编打印的 VA（0x183758440，已含基址），
脚本又加了一次 base，target 变成 0x7fffe3d758440 → 未映射 → 客户端崩溃。
现在：
  · 所有 RVA 都是「VA 减 0x180000000」
  · 调用前先打印 target 并和 SizeOfImage 比对，越界立即中止
  · icall.cmd_call 内部也加了同样的越界拦截
  · 加 --dry 只验地址不调用

不调用 GetActiveMode：它是实例方法，rcx 需要真实对象，传 0 可能内部解引用崩。
模式参数直接试 2（EndlessType.Openworld，服务端日志里 type=2 就是它）。

安全：只读 + 只投递调用，不写任何内存。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402
import wmpick as W  # noqa: E402

RVA_GET_META = 0x3506220     # GetOWEndlessGroupMetaByKey(int)
RVA_NAME_HASH = 0x5DABE70    # NGODNLMBIEL.BNCMBEGMMAN
RVA_RESOLVE = 0x447C090      # BMKMGBALPKO.EJDCEEKDDGL(hash, mode)
MODE = 2                     # EndlessType.Openworld
LEVELS = (21, 22, 23, 24, 31, 32, 33, 34, 35)


def main():
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        if not st or st.get("pid") != pid:
            print("信箱未装/失效，先跑: wmpick.py arm")
            return 1
        mb = st["mailbox"]

        # 先验地址，再投递。icall.cmd_call 里也有同样的检查，这里提前打印。
        span = icall.module_span()
        print("base=%#x  SizeOfImage=%#x" % (base, span or 0))
        bad_addr = False
        for name, rva in (("GetOWEndlessGroupMetaByKey", RVA_GET_META),
                          ("BNCMBEGMMAN", RVA_NAME_HASH),
                          ("EJDCEEKDDGL", RVA_RESOLVE)):
            ok = bool(span) and rva < span
            print("  %-26s rva=%#010x  target=%#x  %s"
                  % (name, rva, base + rva, "ok" if ok else "OUT OF MODULE - 拒绝调用"))
            if not ok:
                bad_addr = True
        if bad_addr:
            print("地址不合法，中止。")
            return 1
        if "--dry" in sys.argv:
            print("（--dry：只验地址，未调用）")
            return 0

        print()
        print("%-5s %-12s %-12s %-12s %s"
              % ("level", "meta", "nameHash", "name(ptr)", "verdict"))
        print("-" * 66)
        bad = []
        for lv in LEVELS:
            meta = W.call(h, base, mb, RVA_GET_META, lv)
            if not meta:
                print("%-5d %-12s %-12s %-12s %s" % (lv, "0", "-", "-", "meta NULL"))
                bad.append(lv)
                continue
            nh = W.call(h, base, mb, RVA_NAME_HASH, meta)
            nm = W.call(h, base, mb, RVA_RESOLVE, nh if nh else 0, MODE)
            ok = bool(nm)
            print("%-5d %-12s %-12s %-12s %s"
                  % (lv, "%#x" % meta, nh if nh is not None else "?",
                     "%#x" % nm if nm else "0",
                     "OK" if ok else "NULL -> RefreshPlayerGroup 会炸"))
            if not ok:
                bad.append(lv)
        print("-" * 66)
        if bad:
            print("不安全档位: %s" % ", ".join(str(x) for x in bad))
        else:
            print("全部安全：这条链上每一步都非空")
        return 0
    finally:
        icall.k32.CloseHandle(h)


if __name__ == "__main__":
    sys.exit(main())
