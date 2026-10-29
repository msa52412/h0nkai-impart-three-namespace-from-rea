# -*- coding: utf-8 -*-
"""inspect_ow —— 只读检查 OWEndlessModule 的运行期状态

不调用任何游戏函数，只读内存，用来回答一个问题：
`baseDataList` 里到底有没有「模式能匹配上」的 EndlessBaseData。

字段偏移来自 `OWEndlessModule.GetCurrentEndlessData` 的反汇编（0x1818981B0）：
    [rbx+0x58]  TwoEndless_k_BackingField
    [rbx+0x68]  baseDataList

il2cpp 的 List<T> 布局：
    +0x00 klass   +0x08 monitor   +0x10 _items   +0x18 _size   +0x20 _version
    _items 是 T[]，元素数据从 +0x20 开始，每元素 8 字节（引用类型）

用法:
    python inspect_ow.py 0x70059d9ddd0
"""
import struct
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402

OFF_TWO_ENDLESS = 0x58
OFF_BASE_LIST = 0x68
LIST_ITEMS = 0x10
LIST_SIZE = 0x18


def q(h, va):
    b = icall.read_mem(h, va, 8)
    if not b or len(b) != 8:
        return None
    return struct.unpack("<Q", b)[0]


def dump(h, va, n, label):
    b = icall.read_mem(h, va, n)
    if not b:
        print("  %s %#x 读取失败" % (label, va))
        return
    print("  %s @%#x:" % (label, va))
    for i in range(0, len(b), 16):
        chunk = b[i:i + 16]
        print("    +%02x  %-47s  %s" % (
            i, chunk.hex(" "),
            "".join(chr(c) if 32 <= c < 127 else "." for c in chunk)))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    this = int(sys.argv[1], 0)
    h, pid, base = icall.open_game()
    if not h:
        print("游戏未运行")
        return 1
    try:
        print("OWEndlessModule this = %#x" % this)
        klass = q(h, this)
        print("  [this] klass = %#x" % (klass or 0))
        if not klass:
            print("  ✗ klass 为 0，this 无效")
            return 1

        te = q(h, this + OFF_TWO_ENDLESS)
        print("  [+%#x] TwoEndless = %#x" % (OFF_TWO_ENDLESS, te or 0))
        if te:
            dump(h, te, 0x40, "TwoEndless")
            inner = q(h, te + 0x10)
            print("    [+0x10] = %#x %s" % (inner or 0,
                                            "（null → GetActiveMode 会走默认分支）" if not inner else ""))

        lst = q(h, this + OFF_BASE_LIST)
        print("  [+%#x] baseDataList = %#x" % (OFF_BASE_LIST, lst or 0))
        if not lst:
            print("  ✗ baseDataList 为 null → GetCurrentEndlessData 必抛 NRE")
            return 0

        items = q(h, lst + LIST_ITEMS)
        raw_size = icall.read_mem(h, lst + LIST_SIZE, 8)
        size = struct.unpack("<Q", raw_size)[0] if raw_size else -1
        print("    _items = %#x   _size = %d" % (items or 0, size))

        if size == 0:
            print("    ✗ 列表为空 → GetCurrentEndlessData 返回 null → SetupView 抛 NRE")
            return 0

        arr_klass = q(h, items) if items else 0
        arr_len_raw = icall.read_mem(h, items + 0x18, 8) if items else None
        arr_len = struct.unpack("<Q", arr_len_raw)[0] if arr_len_raw else -1
        print("    T[] klass = %#x   length = %d" % (arr_klass or 0, arr_len))

        for i in range(min(size, 8)):
            elem = q(h, items + 0x20 + i * 8)
            if not elem:
                print("    [%d] null" % i)
                continue
            ek = q(h, elem)
            print("    [%d] elem=%#x  klass=%#x" % (i, elem, ek or 0))
            dump(h, elem, 0x30, "      elem[%d]" % i)
    finally:
        icall.k32.CloseHandle(h)
    return 0


if __name__ == "__main__":
    sys.exit(main())
