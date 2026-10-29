# -*- coding: utf-8 -*-
"""metaprobe.py — 直接调客户端 GetOWEndlessGroupMetaByKey(level)，看这张表里到底有哪些档位。

为什么需要：
  ClientSafeLevels 只放了 21~24，因为 17:48 下发 35 时
  RefreshPlayerGroup+0x404 拿到 null 元数据抛 NRE（黑屏 + 120 次/秒）。
  但 get_GroupName 的实测显示 31/32/33 能返回正确段位名，
  说明「客户端表有 31~33，没有 34/35」——需要直接验证指针是否为 null。

安全：只读，不写任何内存。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402
import wmpick as W  # noqa: E402

RVA_GET_META = 0x3506220    # OWEndlessGroupMetaReaderExtend.GetOWEndlessGroupMetaByKey(int)
LEVELS = (11, 12, 13, 14, 21, 22, 23, 24, 31, 32, 33, 34, 35, 41, 45)


def main():
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        if not st or st.get('pid') != pid:
            print('信箱未装/失效，先跑: wmpick.py arm')
            return 1
        mb = st['mailbox']

        print('%-6s %-16s %s' % ('level', 'meta ptr', 'verdict'))
        print('-' * 46)
        for lv in LEVELS:
            meta = W.call(h, base, mb, RVA_GET_META, lv)
            if meta and meta > 0x10000:
                verdict = 'OK  (meta exists)'
            else:
                verdict = 'NULL -> 下发表里没有这一行'
            print('%-6d %-16s %s' % (lv, ('%#x' % meta) if meta else '0', verdict))
        return 0
    finally:
        icall.k32.CloseHandle(h)


if __name__ == '__main__':
    sys.exit(main())
