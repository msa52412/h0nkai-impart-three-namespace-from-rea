# -*- coding: utf-8 -*-
"""groupname.py — 直接问客户端：21/22/23/24/31..35 分别显示成哪个段位名。

做法：Client 的 GroupInfo.get_GroupName() 只读 this+0x24（group_level）
      再查 OWEndlessGroupMeta。所以把 +0x24 临时改成各档位、调一次、读回
      MonoString，就能在不改服务端、不让玩家重进的情况下得到真实映射。

安全：只改 GroupInfo+0x24 这一处 4 字节，循环结束立刻还原原值。
      每次调用都投递到游戏主线程同步执行，不会并发渲染。
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402
import wmpick as W  # noqa: E402

RVA_GET_GROUPNAME = 0xEF9320
LEVELS = (21, 22, 23, 24, 31, 32, 33, 34, 35)


def read_cs_string(h, va):
    """il2cpp MonoString: +0x10 = length(int32), +0x14 = utf-16 chars."""
    if not va:
        return None
    hdr = icall.read_mem(h, va, 0x14)
    if not hdr:
        return None
    n = struct.unpack_from('<i', hdr, 0x10)[0]
    if n < 0 or n > 512:
        return None
    data = icall.read_mem(h, va + 0x14, n * 2)
    if not data:
        return None
    return data.decode('utf-16-le', 'replace')


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

        mod = W.call(h, base, mb, W.RVA_GET_MODULE, 0)
        g = W.call(h, base, mb, W.RVA_GET_GROUP, mod)
        print('module = %#x   group = %#x' % (mod or 0, g or 0))
        if not g:
            print('还没进过迪拉克，get_Group() 为空')
            return 1

        orig = W.i32(h, g + 0x24)
        print('group+0x24 = %d' % orig)
        cur = read_cs_string(h, W.call(h, base, mb, RVA_GET_GROUPNAME, g))
        print('当前显示名 = %r' % cur)
        print('-' * 40)

        try:
            for lv in LEVELS:
                icall.write_mem(h, g + 0x24, struct.pack('<i', lv))
                r = W.call(h, base, mb, RVA_GET_GROUPNAME, g)
                print('group_level=%2d -> %r' % (lv, read_cs_string(h, r)))
        finally:
            icall.write_mem(h, g + 0x24, struct.pack('<i', orig))
            print('-' * 40)
            print('已还原 group+0x24 = %d' % orig)
        return 0
    finally:
        icall.k32.CloseHandle(h)


if __name__ == '__main__':
    sys.exit(main())
