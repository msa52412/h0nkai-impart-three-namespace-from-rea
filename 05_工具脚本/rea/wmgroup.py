# -*- coding: utf-8 -*-
"""wmgroup —— 搞清楚 OWEndlessModule.get_Group() 到底是「读缓存」还是「懒创建」

要回答的问题
------------
17:32 进入迪拉克后读到 get_Group() = GroupId 1 / GroupLevel 21 / CurTop 22
17:57 重启后（没进过模式）读到 0 / 0 / 0

两种解释：
  A. 客户端真的拒绝了服务端下发的数据 → 必须继续修服务端
  B. get_Group 是懒创建，_group 只有真正进入模式才被填充 → 0 是正常的，
     之前「客户端静默拒绝」的结论是错的，wmready 的门禁② 是个死循环

判据：反汇编 get_Group，看它在 _group == null 时会不会 new 一个空对象。

用法
----
  python wmgroup.py            反汇编 get_Group / get_module
  python wmgroup.py live       现场读模块的 _group 指针 + 关键字段
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402
import wmpick as W  # noqa: E402
from wmfeat import disasm  # noqa: E402


def cmd_offline():
    disasm(W.RVA_GET_GROUP, "OWEndlessModule.get_Group")
    disasm(W.RVA_GET_MODULE, "get_module")
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

        mod = W.call(h, base, mb, W.RVA_GET_MODULE, 0)
        print("module = %#x" % (mod or 0))
        if not mod:
            return 1

        g = W.call(h, base, mb, W.RVA_GET_GROUP, mod)
        print("get_Group() = %#x" % (g or 0))

        # 模块对象里扫一遍，看有没有 21/22 这种值（服务端下发的档位）
        raw = icall.read_mem(h, mod + 0x10, 0x100)
        if raw:
            hits = []
            for off in range(0, len(raw) - 4, 4):
                v = struct.unpack_from("<i", raw, off)[0]
                if v in (1, 21, 22, 20, 7):
                    hits.append("+%#04x=%d" % (off + 0x10, v))
            print("module 内 0x10~0x110 命中(1/21/22/20/7): %s"
                  % (", ".join(hits) if hits else "无"))

        if g:
            print("group +0x20 GroupId   = %d" % W.i32(h, g + 0x20))
            print("group +0x24 Level     = %d" % W.i32(h, g + 0x24))
            print("group +0x28 CurTop    = %d" % W.i32(h, g + 0x28))
        return 0
    finally:
        icall.k32.CloseHandle(h)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "live":
        return cmd_live()
    return cmd_offline()


if __name__ == "__main__":
    sys.exit(main())
