# -*- coding: utf-8 -*-
"""qtbossdump —— 只读探针：dump 量子/迪拉克 layer0 的 bossGroup 与 monsterGroupList 全字段

目的：判断「运行时改 _bossGroupID / bossGroup」是否可行
  若量子 bossGroup 指针指向的是真实 MonsterGroup 对象（klass 正确、areaName/luaFilePath 合理），
  则只需改 groupID/areaName 等 int/ptr 字段即可，零分配、低风险；
  若指向空壳或垃圾，则必须新建对象（高分配风险）。

纯字段读，不调用任何客户端方法（仅取 OWEndlessModule 静态单例）。

偏移依据（MoleMole.cs）：
  MonsterGroup +0x10 useNewAlgo(bool) / +0x14 groupID / +0x18 maxScore
               +0x1C MonsterInitType / +0x20 MonsterScoreRatio(float)
               +0x28 areaName(string*) / +0x30 isBoss(bool) / +0x34 bossID
               +0x38 canBossRefresh(bool) / +0x3C environmentID
               +0x40 monsterIDList(List<int>) / +0x48 monsterNature
               +0x50 uniqueIDList(int[]) / +0x58 luaFilePath(string*)
               +0x60 isFinish / +0x61 isInvade / +0x62 usCustomAmount
               +0x64 customMonsterNum / +0x68 invadeActiveTime / +0x6C invaderID
               +0x70 buffIDList(List<int>)
  il2cpp string: +0x10 length(int) / +0x14 chars(utf16)
"""
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


def u32(h, a):
    r = icall.read_mem(h, a, 4)
    return struct.unpack("<I", r)[0] if r and len(r) == 4 else None


def f32(h, a):
    r = icall.read_mem(h, a, 4)
    return struct.unpack("<f", r)[0] if r and len(r) == 4 else None


def u8(h, a):
    r = icall.read_mem(h, a, 1)
    return r[0] if r and len(r) == 1 else None


def cstr(h, p):
    """il2cpp System.String -> python str"""
    if not p or not (0x10000 < p < 0x0000800000000000):
        return None
    n = i32(h, p + 0x10)
    if n is None or n < 0 or n > 400:
        return "<len=%s>" % n
    if n == 0:
        return ""
    raw = icall.read_mem(h, p + 0x14, n * 2)
    if not raw or len(raw) != n * 2:
        return "<read fail>"
    try:
        return raw.decode("utf-16-le", "replace")
    except Exception:
        return "<decode fail>"


def lst(h, addr):
    if not addr:
        return 0, 0, []
    arr = u64(h, addr + 0x10)
    n = i32(h, addr + 0x18)
    if not arr or n is None or n < 0 or n > 500:
        return arr, n or 0, []
    return arr, n, [u64(h, arr + 0x20 + i * 8) for i in range(n)]


def ilist_int(h, addr, limit=20):
    """List<int> / int[] -> [int]"""
    if not addr:
        return [], 0
    n = i32(h, addr + 0x18)
    if n is None or n < 0 or n > 500:
        return [], 0
    p = u64(h, addr + 0x10)
    base = (p + 0x20) if (p and 0x10000 < p < 0x0000800000000000) else (addr + 0x20)
    return [i32(h, base + i * 4) for i in range(min(n, limit))], n


def klass(h, obj):
    return u64(h, obj) if obj else 0


def dump_mg(h, obj, tag, indent="      "):
    """dump 一个 MonsterGroup（0x78 字节）"""
    if not obj or not (0x10000 < obj < 0x0000800000000000):
        print("%s%s = %#x  <无效指针>" % (indent, tag, obj or 0))
        return
    print("%s%s = %#x  klass=%#x" % (indent, tag, obj, klass(h, obj)))
    print("%s  useNewAlgo=%s groupID=%s maxScore=%s InitType=%s ScoreRatio=%s"
          % (indent, u8(h, obj + 0x10), i32(h, obj + 0x14), i32(h, obj + 0x18),
             i32(h, obj + 0x1C), f32(h, obj + 0x20)))
    print("%s  areaName=%r  luaFilePath=%r"
          % (indent, cstr(h, u64(h, obj + 0x28)), cstr(h, u64(h, obj + 0x58))))
    print("%s  isBoss=%s bossID=%s canBossRefresh=%s envID=%s"
          % (indent, u8(h, obj + 0x30), i32(h, obj + 0x34), u8(h, obj + 0x38),
             i32(h, obj + 0x3C)))
    mid, mn = ilist_int(h, u64(h, obj + 0x40))
    uid, un = ilist_int(h, u64(h, obj + 0x50))
    bid, bn = ilist_int(h, u64(h, obj + 0x70))
    print("%s  monsterIDList(n=%d)=%s  uniqueIDList(n=%d)=%s  buffIDList(n=%d)=%s"
          % (indent, mn, mid, un, uid, bn, bid))
    print("%s  monsterNature=%s isFinish=%s isInvade=%s usCustomAmount=%s customMonsterNum=%s"
          % (indent, i32(h, obj + 0x48), u8(h, obj + 0x60), u8(h, obj + 0x61),
             u8(h, obj + 0x62), i32(h, obj + 0x64)))
    print("%s  invadeActiveTime=%s invaderID=%s"
          % (indent, u32(h, obj + 0x68), u32(h, obj + 0x6C)))


def get_module(h, base):
    st = icall.load_state()
    mb = st["mailbox"]
    if icall.cmd_call(base + RVA_GET_MODULE, [0], 5.0) != 0:
        return 0
    return u64(h, mb + 0x30)


def main():
    h, pid, base = icall.open_game()
    if not h:
        print("X 打不开游戏进程")
        return 1
    try:
        print("pid=%d base=%#x" % (pid, base))
        mod = get_module(h, base)
        if not mod:
            print("X get_module=0")
            return 1
        print("OWEndlessModule = %#x\n" % mod)

        bdl = u64(h, mod + OFF_BASEDATA)
        _, n, items = lst(h, bdl)
        print("_baseDataList size=%d\n" % n)

        for ebd in items:
            if not ebd:
                continue
            mode = i32(h, ebd + 0x10)
            bli = u64(h, ebd + 0x28)
            if not bli:
                continue
            abil = u64(h, bli + 0x88)
            _, L_n, L_items = lst(h, abil)
            print("========== Mode=%d  layers=%d ==========" % (mode, L_n))
            for j, li in enumerate(L_items[:2]):        # 只看前两层
                if not li:
                    continue
                print("  --- layer[%d]  LayerInfo=%#x ---" % (j, li))
                print("      _layerIndex=%s _monsterAreaID=%s _bossAreaID=%s"
                      % (i32(h, li + 0x10), i32(h, li + 0x14), i32(h, li + 0x18)))
                print("      _scoreConfigID=%s _environmentID=%s _buffID=%s"
                      % (i32(h, li + 0x1C), i32(h, li + 0x20), i32(h, li + 0x24)))
                print("      _monsterType=%s _areaConfig=%#x _environmentConfig=%#x"
                      % (i32(h, li + 0x38), u64(h, li + 0x40), u64(h, li + 0x48)))

                # _monsterConfigList
                _, mc_n, _ = lst(h, u64(h, li + 0x58))
                # _monsterGroupIDList
                gids, gid_n = ilist_int(h, u64(h, li + 0x60))
                print("      _monsterConfigList n=%d  _monsterGroupIDList n=%d %s"
                      % (mc_n, gid_n, gids))

                # monsterGroupList
                mgp = u64(h, li + 0x70)
                _, mg_n, mg_items = lst(h, mgp)
                print("      monsterGroupList = %#x  n=%d" % (mgp, mg_n))
                for k, mo in enumerate(mg_items[:6]):
                    dump_mg(h, mo, "[%d]" % k, "        ")

                # bossGroup
                bg = u64(h, li + 0x78)
                print("      _bossGroupID = %s" % i32(h, li + 0x68))
                dump_mg(h, bg, "bossGroup", "        ")
            print()
        return 0
    finally:
        icall.k32.CloseHandle(h)


if __name__ == "__main__":
    sys.exit(main() or 0)
