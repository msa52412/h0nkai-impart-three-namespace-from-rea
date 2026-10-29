# -*- coding: utf-8 -*-
"""qtprobe2 —— 调用 QTInLevelData 的只读 getter，拿到客户端真正构建出的 MonsterGroup

RVA = 反编译注释里的绝对地址 - 0x180000000
  get_monsterGroupIndex   @0x1811F1D30 -> 0x11F1D30
  MonsterGroupCount       @0x1811F13D0 -> 0x11F13D0
  MonsterGroupToIndex     @0x1811F1440 -> 0x11F1440
  GetCurrentEnv           @0x1811F0B00 -> 0x11F0B00
  get_monsterGroupDetail  @0x1811F1CB0 -> 0x11F1CB0

MonsterGroup 布局（MoleMole.cs 02002568）:
  +0x14 groupID | +0x18 maxScore | +0x1C MonsterInitType | +0x28 areaName(str*)
  +0x30 isBoss | +0x34 bossID | +0x38 canBossRefresh | +0x3C environmentID
  +0x40 monsterIDList | +0x48 monsterNature | +0x58 luaFilePath(str*)
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402

RVA_GET_MODULE = 0x1A92080
OFF_QT = 0xC0

RVA_GET_GROUP_INDEX = 0x11F1D30
RVA_GROUP_COUNT = 0x11F13D0
RVA_GROUP_TO_INDEX = 0x11F1440
RVA_CUR_ENV = 0x11F0B00
RVA_GROUP_DETAIL = 0x11F1CB0


def u64(h, a):
    r = icall.read_mem(h, a, 8)
    return struct.unpack("<Q", r)[0] if r and len(r) == 8 else None


def i32(h, a):
    r = icall.read_mem(h, a, 4)
    return struct.unpack("<i", r)[0] if r and len(r) == 4 else None


def rd_str(h, p):
    if not p or p < 0x10000:
        return None
    head = icall.read_mem(h, p + 0x10, 4)
    if not head or len(head) != 4:
        return None
    n = struct.unpack("<i", head)[0]
    if n <= 0 or n > 512:
        return "<len=%d>" % n
    s = icall.read_mem(h, p + 0x14, n * 2)
    if not s:
        return None
    try:
        return s.decode("utf-16-le", "replace")
    except Exception:
        return None


def call(h, base, st, rva, args, timeout=5.0, label=""):
    if icall.cmd_call(base + rva, args, timeout) != 0:
        print("  ✗ %s 调用失败" % label)
        return None
    return u64(h, st["mailbox"] + 0x30)


def main():
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        mod = call(h, base, st, RVA_GET_MODULE, [0], 5.0, "get_module")
        if not mod:
            return 1
        qt = u64(h, mod + OFF_QT)
        print("pid=%d base=%#x" % (pid, base))
        print("OWEndlessModule=%#x  qtInLevelData=%#x" % (mod, qt or 0))
        if not qt:
            return 2

        grp = i32(h, qt + 0x14)
        print("\n[QTInLevelData] _monsterGroup=%s _progress=%s" % (grp, i32(h, qt + 0x3C)))

        def as_i(v):
            return None if v is None else struct.unpack("<i", struct.pack("<I", v & 0xFFFFFFFF))[0]

        cnt = call(h, base, st, RVA_GROUP_COUNT, [qt], 5.0, "MonsterGroupCount")
        print("MonsterGroupCount()      = %s" % as_i(cnt))

        idx = call(h, base, st, RVA_GET_GROUP_INDEX, [qt], 5.0, "get_monsterGroupIndex")
        print("get_monsterGroupIndex()  = %s" % as_i(idx))

        ti = call(h, base, st, RVA_GROUP_TO_INDEX, [qt, grp], 5.0, "MonsterGroupToIndex")
        print("MonsterGroupToIndex(%d) = %s" % (grp, as_i(ti)))

        env = call(h, base, st, RVA_CUR_ENV, [qt], 5.0, "GetCurrentEnv")
        print("GetCurrentEnv()          = %#x" % (env or 0))
        if env:
            raw = icall.read_mem(h, env, 0x40)
            if raw:
                for i in range(0, len(raw), 16):
                    ch = raw[i:i + 16]
                    print("    +%02x  %s | %#x %#x" % (
                        i, " ".join("%02x" % b for b in ch),
                        struct.unpack("<Q", ch[:8])[0], struct.unpack("<Q", ch[8:])[0]))

        # 最"重"的一个放最后
        mg = call(h, base, st, RVA_GROUP_DETAIL, [qt], 5.0, "get_monsterGroupDetail")
        print("\nmonsterGroupDetail       = %#x" % (mg or 0))
        if mg:
            print("  groupID          = %s" % i32(h, mg + 0x14))
            print("  maxScore         = %s" % i32(h, mg + 0x18))
            print("  MonsterInitType  = %s" % i32(h, mg + 0x1C))
            print("  areaName         = %r" % rd_str(h, u64(h, mg + 0x28)))
            print("  isBoss           = %s" % (icall.read_mem(h, mg + 0x30, 1) or b"")[0])
            print("  bossID           = %s" % i32(h, mg + 0x34))
            print("  canBossRefresh   = %s" % (icall.read_mem(h, mg + 0x38, 1) or b"")[0])
            print("  environmentID    = %s" % i32(h, mg + 0x3C))
            print("  luaFilePath      = %r" % rd_str(h, u64(h, mg + 0x58)))
            print("  monsterIDList    = %#x" % (u64(h, mg + 0x40) or 0))
            print("  uniqueIDList     = %#x" % (u64(h, mg + 0x50) or 0))
        return 0
    finally:
        icall.k32.CloseHandle(h)


if __name__ == "__main__":
    sys.exit(main() or 0)
