# -*- coding: utf-8 -*-
"""验证 _areaConfig 指向的 OpenWorldArea.areaId（+0x20 裸字段）"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402

RVA_GET_MODULE = 0x1A92080
OFF_BASEDATA = 0x68


def u64(h, a):
    if not a:
        return 0
    r = icall.read_mem(h, a, 8)
    return struct.unpack("<Q", r)[0] if r and len(r) == 8 else 0


def i32(h, a):
    r = icall.read_mem(h, a, 4)
    return struct.unpack("<i", r)[0] if r and len(r) == 4 else None


def lst(h, addr):
    if not addr:
        return 0, 0, []
    arr = u64(h, addr + 0x10)
    n = i32(h, addr + 0x18)
    if not arr or n is None or n < 0 or n > 500:
        return arr, n or 0, []
    return arr, n, [u64(h, arr + 0x20 + i * 8) for i in range(n)]


def main():
    h, pid, base = icall.open_game()
    if not h:
        print("X")
        return 1
    try:
        st = icall.load_state()
        if icall.cmd_call(base + RVA_GET_MODULE, [0], 5.0) != 0:
            print("X call")
            return 1
        mod = u64(h, st["mailbox"] + 0x30)
        _, n, items = lst(h, u64(h, mod + OFF_BASEDATA))
        for ebd in items:
            if not ebd:
                continue
            mode = i32(h, ebd + 0x10)
            bli = u64(h, ebd + 0x28)
            if not bli:
                continue
            _, L_n, L_items = lst(h, u64(h, bli + 0x88))
            print("=== Mode=%d layers=%d ===" % (mode, L_n))
            for j, li in enumerate(L_items):
                if not li:
                    continue
                ac = u64(h, li + 0x40)
                ec = u64(h, li + 0x48)
                print("  layer[%d] _monsterAreaID=%s _bossAreaID=%s"
                      % (j, i32(h, li + 0x14), i32(h, li + 0x18)))
                print("          _areaConfig=%#x  -> areaId=%s  klass=%#x"
                      % (ac, i32(h, ac + 0x20) if ac else None, u64(h, ac) if ac else 0))
                print("          _environmentConfig=%#x" % (ec or 0))
        return 0
    finally:
        icall.k32.CloseHandle(h)


if __name__ == "__main__":
    sys.exit(main() or 0)
