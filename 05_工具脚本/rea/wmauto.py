# -*- coding: utf-8 -*-
"""wmauto —— 等管理器实例出现，然后自动跑 setup

为什么需要它
------------
`SetupAllEntryButton` 只在**面板装配时**被调用一次，所以管理器实例必须等
用户在游戏里打开一次世界地图才会被钩子抓到。手动流程是：
    开面板 -> 回来跑 setup -> 再点卡
中间那次「回来跑」纯属等待，可以自动化。

本脚本每秒轮询信箱的 MGR_SLOT（page+0x48），一旦非 0 就立刻调用
`wmpick.cmd_setup()`（相当于 setup --yes）。

用法
----
    python wmauto.py           最多等 300 秒
    python wmauto.py 600       最多等 600 秒

安全
----
轮询阶段只读。抓到之后执行的就是 setup 的全部动作：
  1) 解锁补丁  5 字节（LJMINEONAFF 内，可还原）
  2) 点击接线  stub 写进自建区 + 覆盖 DoClickAction 入口 14 字节（可还原）
**不写任何 il2cpp 托管对象内存**（FeatureType 那步已永久移除）。
"""
import os
import struct
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402
import wmpick as W  # noqa: E402


def wait_mgr(timeout=300.0):
    """轮询 MGR_SLOT，返回管理器实例地址（0 表示超时）。"""
    deadline = time.time() + timeout
    last = None
    dots = 0
    while time.time() < deadline:
        h, pid, base = icall.open_game()
        if not h:
            print("\n✗ 找不到游戏进程")
            return 0
        try:
            st = icall.load_state()
            if not st or st.get("pid") != pid:
                print("\n✗ 信箱与当前进程不匹配，先跑 python wmpick.py arm")
                return 0
            raw = icall.read_mem(h, st["page"] + W.MGR_SLOT, 8)
            mgr = struct.unpack("<Q", raw)[0] if raw and len(raw) == 8 else 0
            if mgr:
                print("\n✓ 抓到管理器实例 %#x" % mgr)
                return mgr
        finally:
            icall.k32.CloseHandle(h)
        dots += 1
        sys.stdout.write(".")
        sys.stdout.flush()
        if dots % 60 == 0:
            print(" %ds" % int(timeout - (deadline - time.time())))
        last = time.time()
        time.sleep(1.0)
    print("\n✗ 等待超时（%.0fs），管理器实例始终为空" % timeout)
    return 0


def main():
    timeout = 300.0
    if len(sys.argv) > 1:
        try:
            timeout = float(sys.argv[1])
        except ValueError:
            pass
    print("等你在游戏里打开「世界地图 -> 挑战」面板（最多 %.0fs）…" % timeout)
    if not wait_mgr(timeout):
        print("  面板打开后重跑本脚本即可。")
        return 1
    # 给管理器一点时间把卡片列表填完
    time.sleep(0.6)
    if "--yes" not in sys.argv:
        sys.argv.append("--yes")
    print()
    return W.cmd_setup()


if __name__ == "__main__":
    sys.exit(main())
