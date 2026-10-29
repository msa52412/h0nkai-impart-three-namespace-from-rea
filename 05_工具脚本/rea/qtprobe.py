# -*- coding: utf-8 -*-
"""qtprobe —— 只读：从 OWEndlessModule.qtInLevelData 读客户端当前认同的组/进度

偏移依据（反编译 MoleMole.cs）：
  OWEndlessModule + 0xC0 = qtInLevelData
  QTInLevelData   + 0x10 = _areaScoreConfigId
                  + 0x14 = _monsterGroup (BackingField)
                  + 0x18 = _battleConfig (ptr)
                  + 0x34 = _extraScore
                  + 0x3C = _progress
                  + 0x40 = _randomSeed
                  + 0x48 = _module
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402

RVA_GET_MODULE = 0x1A92080
OFF_QT = 0xC0
OFF_TWO_ENDLESS = 0x58
OFF_BASEDATA = 0x68


def u64(h, a):
    r = icall.read_mem(h, a, 8)
    return struct.unpack("<Q", r)[0] if r and len(r) == 8 else None


def i32(h, a):
    r = icall.read_mem(h, a, 4)
    return struct.unpack("<i", r)[0] if r and len(r) == 4 else None


def u32(h, a):
    r = icall.read_mem(h, a, 4)
    return struct.unpack("<I", r)[0] if r and len(r) == 4 else None


def get_module(h, base):
    st = icall.load_state()
    mb = st["mailbox"]
    if icall.cmd_call(base + RVA_GET_MODULE, [0], 5.0) != 0:
        return None
    return u64(h, mb + 0x30)


def dump(h, addr, n, title):
    print("\n--- %s @ %#x (%d B) ---" % (title, addr, n))
    raw = icall.read_mem(h, addr, n)
    if not raw:
        print("  <读不到>")
        return
    for i in range(0, len(raw), 16):
        chunk = raw[i:i + 16]
        hexs = " ".join("%02x" % b for b in chunk)
        qs = struct.unpack("<QQ", chunk) if len(chunk) == 16 else None
        extra = ("  | %#x %#x" % qs) if qs else ""
        print("  +%03x  %-47s%s" % (i, hexs, extra))


def main():
    h, pid, base = icall.open_game()
    if not h:
        print("✗ 打不开游戏进程")
        return 1
    try:
        print("pid=%d base=%#x" % (pid, base))
        mod = get_module(h, base)
        if not mod:
            print("✗ get_module=0")
            return 1
        print("OWEndlessModule = %#x" % mod)

        te = u64(h, mod + OFF_TWO_ENDLESS)
        print("TwoEndless      = %#x" % (te or 0))
        bd = u64(h, mod + OFF_BASEDATA)
        print("_baseDataList   = %#x" % (bd or 0))

        qt = u64(h, mod + OFF_QT)
        print("qtInLevelData   = %#x" % (qt or 0))
        if not qt:
            print("!! qtInLevelData 为空 —— 客户端没进量子路径")
            return 2

        dump(h, qt, 0x60, "QTInLevelData")
        print("\n=== 解读 ===")
        print("  _areaScoreConfigId = %s   (期望 2001)" % i32(h, qt + 0x10))
        print("  _monsterGroup      = %s   (期望 10400)" % i32(h, qt + 0x14))
        print("  _battleConfig      = %#x" % (u64(h, qt + 0x18) or 0))
        print("  _extraScore        = %s" % i32(h, qt + 0x34))
        print("  _progress          = %s" % i32(h, qt + 0x3C))
        print("  _randomSeed        = %s" % u32(h, qt + 0x40))
        print("  _module            = %#x  (应等于 %#x)" % (u64(h, qt + 0x48) or 0, mod))
        return 0
    finally:
        icall.k32.CloseHandle(h)


if __name__ == "__main__":
    sys.exit(main() or 0)
