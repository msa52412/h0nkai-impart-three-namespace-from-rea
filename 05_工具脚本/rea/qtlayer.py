# -*- coding: utf-8 -*-
"""qtlayer —— 只读探针：读 OWEndLessBattleLevelInfo 的层信息构建结果

判决点：_areaBattleInfoList._size
  = 1  -> 量子多层盘只建出 1 层信息，layer>=1 无 info，切层必然失败
  = 4  -> 层信息齐全，问题不在层构建

偏移依据（反编译 MoleMole.cs，纯字段读，不调用任何客户端方法）：
  OWEndlessModule            +0x68 _baseDataList : List<EndlessBaseData>
  EndlessBaseData            +0x10 Mode / +0x28 _BattleLevelInfo
  OWEndLessBattleLevelInfo   +0x20 currentEnterLayerIndex
                             +0x28 _areaList / +0x30 _bossAreaIDList
                             +0x38 _maxLayerIndex / +0x68 _environmentIDList
                             +0x74 _scoreConfigID / +0x78 _areaCount
                             +0x7C _groupLevel / +0x80 _groupHardLevel
                             +0x88 _areaBattleInfoList : List<OWEndLessLayerInfo>
  OWEndLessLayerInfo         +0x10 _layerIndex / +0x14 _monsterAreaID / +0x18 _bossAreaID
                             +0x1C _scoreConfigID / +0x20 _environmentID / +0x24 _buffID
                             +0x68 _bossGroupID / +0x70 monsterGroupList / +0x78 bossGroup
                             +0x40 _areaConfig
  List<T>                    +0x10 _items(Il2CppArray*) / +0x18 _size
  Il2CppArray                +0x20 vector 起点
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402

RVA_GET_MODULE = 0x1A92080
OFF_BASEDATA = 0x68
OFF_QT = 0xC0


def u64(h, a):
    r = icall.read_mem(h, a, 8)
    return struct.unpack("<Q", r)[0] if r and len(r) == 8 else None


def i32(h, a):
    r = icall.read_mem(h, a, 4)
    return struct.unpack("<i", r)[0] if r and len(r) == 4 else None


def u32(h, a):
    r = icall.read_mem(h, a, 4)
    return struct.unpack("<I", r)[0] if r and len(r) == 4 else None


def lst(h, addr):
    """List<T> -> (items_ptr, size, [element ptrs])"""
    if not addr:
        return 0, 0, []
    arr = u64(h, addr + 0x10)
    n = i32(h, addr + 0x18)
    if not arr or n is None or n < 0 or n > 500:
        return arr or 0, n or 0, []
    items = []
    for i in range(n):
        items.append(u64(h, arr + 0x20 + i * 8))
    return arr, n, items


def iarr(h, addr):
    """IList<int> / int[] / List<int> -> [int]；size 统一在 +0x18
    int[]  : 元素直接在 addr+0x20，步长 4（+0x10 是 bounds，不是 _items）
    List<int>: +0x10 = _items(数组)，元素在 arr+0x20，步长 4"""
    if not addr:
        return [], 0
    n = i32(h, addr + 0x18)
    if n is None or n < 0 or n > 500:
        return [], 0
    p = u64(h, addr + 0x10)
    if p and 0x10000 < p < 0x0000800000000000:      # 像 List<T>：跳一层数组
        base = p + 0x20
    else:
        base = addr + 0x20                           # 就是 int[]
    vals = []
    for i in range(n):
        vals.append(i32(h, base + i * 4))
    return vals, n


def get_module(h, base):
    st = icall.load_state()
    mb = st["mailbox"]
    if icall.cmd_call(base + RVA_GET_MODULE, [0], 5.0) != 0:
        return None
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
        print("OWEndlessModule = %#x" % mod)

        bdl = u64(h, mod + OFF_BASEDATA)
        arr, n, items = lst(h, bdl)
        print("_baseDataList   = %#x  size=%d" % (bdl or 0, n))
        if n == 0:
            print("!! 空 —— 先打开旧深渊界面让客户端 Refresh 一次")
            return 2

        for idx, ebd in enumerate(items):
            if not ebd:
                continue
            mode = i32(h, ebd + 0x10)
            bli = u64(h, ebd + 0x28)
            print("\n========== _baseDataList[%d] Mode=%s ==========" % (idx, mode))
            print("  EndlessBaseData = %#x   BattleLevelInfo = %#x" % (ebd, bli or 0))
            if not bli:
                print("  !! BattleLevelInfo 为空（该 mode 未初始化）")
                continue

            area_list = u64(h, bli + 0x28)
            boss_list = u64(h, bli + 0x30)
            env_list = u64(h, bli + 0x68)
            abil = u64(h, bli + 0x88)

            a_vals, a_n = iarr(h, area_list)
            b_vals, b_n = iarr(h, boss_list)
            e_vals, e_n = iarr(h, env_list)
            L_arr, L_n, L_items = lst(h, abil)

            print("  currentEnterLayerIndex = %s" % i32(h, bli + 0x20))
            print("  _maxLayerIndex         = %s   <== 已到达的最大层" % i32(h, bli + 0x38))
            print("  _areaCount             = %s" % i32(h, bli + 0x78))
            print("  _scoreConfigID         = %s" % i32(h, bli + 0x74))
            print("  _groupLevel            = %s" % i32(h, bli + 0x7C))
            print("  _groupHardLevel        = %s" % i32(h, bli + 0x80))
            print("  _areaList              = %#x  size=%d  %s" % (area_list or 0, a_n, a_vals))
            print("  _bossAreaIDList        = %#x  size=%d  %s" % (boss_list or 0, b_n, b_vals))
            print("  _environmentIDList     = %#x  size=%d  %s" % (env_list or 0, e_n, e_vals))
            print("  >>> _areaBattleInfoList= %#x  size=%d   <<< 判决点" % (abil or 0, L_n))

            for j, li in enumerate(L_items):
                if not li:
                    print("    [%d] <null>" % j)
                    continue
                mg_arr, mg_n, _ = lst(h, u64(h, li + 0x70))
                gid_arr, gid_n, _ = lst(h, u64(h, li + 0x60))
                mcfg_arr, mcfg_n, _ = lst(h, u64(h, li + 0x58))
                gids = []
                if gid_arr and gid_n:
                    p = u64(h, u64(h, li + 0x60) + 0x10) or (u64(h, li + 0x60) + 0x20)
                    gids = [i32(h, p + k * 4) for k in range(min(gid_n, 12))]
                print("    [%d] layer=%s monsterArea=%s bossArea=%s env=%s buff=%s "
                      "score=%s bossGroupID=%s areaConfig=%#x" % (
                          j, i32(h, li + 0x10), i32(h, li + 0x14), i32(h, li + 0x18),
                          i32(h, li + 0x20), i32(h, li + 0x24), i32(h, li + 0x1C),
                          i32(h, li + 0x68), u64(h, li + 0x40) or 0))
                print("        _monsterConfigList=%d  _monsterGroupIDList=%d %s  monsterGroupList=%d  bossGroup=%#x" % (
                    mcfg_n, gid_n, gids, mg_n, u64(h, li + 0x78) or 0))

        qt = u64(h, mod + OFF_QT)
        print("\nqtInLevelData = %#x" % (qt or 0))
        if qt:
            print("  _areaScoreConfigId = %s" % i32(h, qt + 0x10))
            print("  _monsterGroup      = %s" % i32(h, qt + 0x14))
        return 0
    finally:
        icall.k32.CloseHandle(h)


if __name__ == "__main__":
    sys.exit(main() or 0)
