# -*- coding: utf-8 -*-
"""qtbossfix —— 运行时修补量子盘 BOSS 组空壳（可回滚）

背景（实测 + 表数据双向确认）：
  OWEndlessAreaScoreConfig(2104).BossScoreConfig = []  -> 客户端 Refresh 时
  仍然 new 了一个 MonsterGroup 对象，但没有任何数据可填，于是得到一个
  全 0 空壳（groupID=0 / InitType=0 / maxScore=0 / areaName=null）。
  BOSS 关因此不知道刷什么，卡在 Loading。

  而 OWEndlessMonsterGroupScore 里 MonsterGroupID=52 的定义是完整的：
      Score=3600  MonsterInitType=2301  RandomType=2
      OWEndlessMonsterInitType(2301): WaveList=[1002] isNegate=true EnvironmentIDList=[]
      QTEndlessMonsterWave(1002): DistRule=[Twin03,Twin03] RankDist=[3,3] -> 2/2 可解析

  所以只要把表里的值抄进那个空壳，就能让 BOSS 关有据可依。

改法（零分配、不改 List 结构、不改代码段）：
  MonsterGroup +0x14 groupID          <- 52
               +0x18 maxScore         <- 3600
               +0x1C MonsterInitType  <- 2301
               +0x30 isBoss           <- 1
               +0x3C environmentID    <- layer0 的 _environmentID (1001)
               +0x28 areaName         <- 借用迪拉克 BOSS 组的字符串指针
               +0x58 luaFilePath      <- 借用迪拉克 BOSS 组的字符串指针
  OWEndLessLayerInfo +0x68 _bossGroupID <- 52

用法：
  python qtbossfix.py            # dry-run，只打印将写入的旧值/新值
  python qtbossfix.py --apply    # 实际写入，并把旧值存到 qtbossfix_backup.json
  python qtbossfix.py --restore  # 从 qtbossfix_backup.json 还原
"""
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402

RVA_GET_MODULE = 0x1A92080
OFF_BASEDATA = 0x68
BACKUP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qtbossfix_backup.json")

TARGET_GROUP_ID = 52
TARGET_SCORE = 3600
TARGET_INIT_TYPE = 2301


def u64(h, a):
    if not a:
        return 0
    r = icall.read_mem(h, a, 8)
    return struct.unpack("<Q", r)[0] if r and len(r) == 8 else 0


def i32(h, a):
    r = icall.read_mem(h, a, 4)
    return struct.unpack("<i", r)[0] if r and len(r) == 4 else None


def u8(h, a):
    r = icall.read_mem(h, a, 1)
    return r[0] if r and len(r) == 1 else None


def lst(h, addr):
    if not addr:
        return 0, 0, []
    arr = u64(h, addr + 0x10)
    n = i32(h, addr + 0x18)
    if not arr or n is None or n < 0 or n > 500:
        return arr, n or 0, []
    return arr, n, [u64(h, arr + 0x20 + i * 8) for i in range(n)]


def get_module(h, base):
    st = icall.load_state()
    mb = st["mailbox"]
    if icall.cmd_call(base + RVA_GET_MODULE, [0], 5.0) != 0:
        return 0
    return u64(h, mb + 0x30)


def find_layers(h):
    """返回 {mode: (battleLevelInfo, [layerInfo...])}"""
    mod = get_module(h, base_g)
    if not mod:
        return {}
    bdl = u64(h, mod + OFF_BASEDATA)
    _, n, items = lst(h, bdl)
    out = {}
    for ebd in items:
        if not ebd:
            continue
        mode = i32(h, ebd + 0x10)
        bli = u64(h, ebd + 0x28)
        if not bli:
            continue
        _, L_n, L_items = lst(h, u64(h, bli + 0x88))
        out[mode] = (bli, L_items)
    return out


def restore(h):
    if not os.path.exists(BACKUP):
        print("X 找不到备份 %s" % BACKUP)
        return 1
    with open(BACKUP, "r", encoding="utf-8") as f:
        bk = json.load(f)
    for e in bk["writes"]:
        va, old_hex, size = e["va"], e["old"], e["size"]
        icall.write_mem(h, va, bytes.fromhex(old_hex))
        cur = icall.read_mem(h, va, size).hex()
        print("  restore %#x  -> %s  %s" % (va, cur, "OK" if cur == old_hex else "MISMATCH"))
    print("已还原 %d 处" % len(bk["writes"]))
    return 0


def main():
    global base_g
    apply = "--apply" in sys.argv
    do_restore = "--restore" in sys.argv

    h, pid, base = icall.open_game()
    if not h:
        print("X 打不开游戏进程")
        return 1
    base_g = base
    try:
        print("pid=%d base=%#x  mode=%s\n" % (pid, base, "APPLY" if apply else ("RESTORE" if do_restore else "DRY-RUN")))

        if do_restore:
            return restore(h)

        layers = find_layers(h)
        if 3 not in layers:
            print("X 没找到 Mode=3（量子）的 BattleLevelInfo —— 请先打开量子奇点准备页")
            return 2
        if 2 not in layers:
            print("X 没找到 Mode=2（迪拉克）—— 需要借用它的 areaName/luaFilePath 字符串指针")
            return 2

        # 迪拉克 layer0 的 BOSS 组，用来借字符串指针
        _, dl = layers[2]
        if not dl:
            print("X 迪拉克无层信息")
            return 2
        dilak_boss = u64(h, dl[0] + 0x78)
        src_area = u64(h, dilak_boss + 0x28) if dilak_boss else 0
        src_lua = u64(h, dilak_boss + 0x58) if dilak_boss else 0
        print("借用源（迪拉克 layer0 bossGroup=%#x）: areaName=%#x luaFilePath=%#x"
              % (dilak_boss, src_area, src_lua))
        if not src_area:
            print("X 借用源 areaName 为空，放弃")
            return 3

        # 量子 layer0
        _, ql = layers[3]
        if not ql:
            print("X 量子无层信息")
            return 2
        li = ql[0]
        env = i32(h, li + 0x20)
        boss = u64(h, li + 0x78)
        print("目标：量子 layer0 LayerInfo=%#x  bossGroup=%#x  env=%s\n" % (li, boss, env))
        if not boss:
            print("X bossGroup 指针为空 —— 这个盘连空壳都没建，无法零分配修补")
            return 3

        print("当前空壳内容：")
        print("  groupID=%s maxScore=%s InitType=%s isBoss=%s envID=%s areaName=%#x lua=%#x"
              % (i32(h, boss + 0x14), i32(h, boss + 0x18), i32(h, boss + 0x1C),
                 u8(h, boss + 0x30), i32(h, boss + 0x3C),
                 u64(h, boss + 0x28), u64(h, boss + 0x58)))
        print("  LayerInfo._bossGroupID = %s\n" % i32(h, li + 0x68))

        # (va, bytes, 说明)
        plan = [
            (boss + 0x14, struct.pack("<i", TARGET_GROUP_ID), "bossGroup.groupID = %d" % TARGET_GROUP_ID),
            (boss + 0x18, struct.pack("<i", TARGET_SCORE), "bossGroup.maxScore = %d" % TARGET_SCORE),
            (boss + 0x1C, struct.pack("<i", TARGET_INIT_TYPE), "bossGroup.MonsterInitType = %d" % TARGET_INIT_TYPE),
            # OWEndlessMonsterInitType(2301).MonsterScoreRatio = 1 —— 空壳是 0.0，
            # lua 的 StartAutoChangeLevelScoreByTime 就是按时间推进分数，分母为 0 极可能是
            # "invalid arguments" 的来源。必须补成表里的 1.0f。
            (boss + 0x20, struct.pack("<f", 1.0), "bossGroup.MonsterScoreRatio = 1.0（表值）"),
            (boss + 0x30, struct.pack("<B", 1), "bossGroup.isBoss = 1"),
            (boss + 0x3C, struct.pack("<i", env), "bossGroup.environmentID = %s" % env),
            (boss + 0x28, struct.pack("<Q", src_area), "bossGroup.areaName <- 迪拉克指针"),
            (boss + 0x58, struct.pack("<Q", src_lua), "bossGroup.luaFilePath <- 迪拉克指针"),
            (li + 0x68, struct.pack("<i", TARGET_GROUP_ID), "LayerInfo._bossGroupID = %d" % TARGET_GROUP_ID),
        ]

        print("计划写入 %d 处：" % len(plan))
        writes = []
        for va, data, desc in plan:
            old = icall.read_mem(h, va, len(data))
            same = old == data
            print("  %#012x  %-42s  %s -> %s %s"
                  % (va, desc, old.hex(), data.hex(), "(已是目标值)" if same else ""))
            writes.append({"va": va, "old": old.hex(), "new": data.hex(), "size": len(data), "desc": desc})

        if not apply:
            print("\n[DRY-RUN] 未写入。确认无误后加 --apply 执行。")
            return 0

        for e in writes:
            icall.write_mem(h, e["va"], bytes.fromhex(e["new"]))
        with open(BACKUP, "w", encoding="utf-8") as f:
            json.dump({"pid": pid, "writes": writes}, f, ensure_ascii=False, indent=2)
        print("\n已写入。备份 -> %s" % BACKUP)

        print("\n回读校验：")
        print("  groupID=%s maxScore=%s InitType=%s isBoss=%s envID=%s areaName=%#x lua=%#x bossGroupID=%s"
              % (i32(h, boss + 0x14), i32(h, boss + 0x18), i32(h, boss + 0x1C),
                 u8(h, boss + 0x30), i32(h, boss + 0x3C),
                 u64(h, boss + 0x28), u64(h, boss + 0x58), i32(h, li + 0x68)))
        print("\n现在直接进 BOSS 关测试。若客户端刷新准备页（Refresh）会覆盖，需重新执行 --apply。")
        return 0
    finally:
        icall.k32.CloseHandle(h)


if __name__ == "__main__":
    sys.exit(main() or 0)
