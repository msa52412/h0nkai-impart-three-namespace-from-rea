# -*- coding: utf-8 -*-
"""qtbossfix2 —— 方案 B：把量子 BOSS 组改成「迪拉克 BOSS 组克隆」（绕开 wave 路径）

动机：
  方案 A（InitType=2301 -> WaveList=[1002]）虽然让倒计时跑起来了，但卡在 lua：
    QuantumEndlessCommon.lua:283
    invalid arguments to method: LevelDesignManager.StartAutoChangeLevelScoreByTime
    in 'loadMonster' <- QuantumEndless.lua:72 <- do_wave
  该 C# 方法签名是 (long initScore, float duration, long finalScore)，
  而相邻的 StartAutoChangeLevelExtraScoreByTime 是 (long, long, float) —— 参数顺序相反，
  典型的 lua/C# 版本错位。lua 在 wave 加载分支里必然抛异常，协程死掉，怪就不刷。

  迪拉克 BOSS 走的是另一条路：InitType=0 + uniqueIDList 直接生成单位，
  不经过 wave / loadMonster 的这段分数逻辑。所以把量子 BOSS 组克隆成迪拉克的样子，
  有机会绕开这个 lua 崩溃点。

改动（全部借用迪拉克 layer0 bossGroup 的指针/值，零分配）：
  bossGroup +0x20 ScoreRatio    <- 迪拉克
  bossGroup +0x1C MonsterInitType <- 迪拉克 (0)
  bossGroup +0x34 bossID        <- 迪拉克 (100038)
  bossGroup +0x50 uniqueIDList  <- 迪拉克指针 ([771])
  保留：groupID=52 / maxScore=3600 / isBoss=1 / envID=1001 / areaName / luaFilePath

用法：python qtbossfix2.py [--apply|--restore]
"""
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402

RVA_GET_MODULE = 0x1A92080
OFF_BASEDATA = 0x68
BACKUP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qtbossfix2_backup.json")


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


def get_layers(h, base):
    st = icall.load_state()
    if icall.cmd_call(base + RVA_GET_MODULE, [0], 5.0) != 0:
        return {}
    mod = u64(h, st["mailbox"] + 0x30)
    _, n, items = lst(h, u64(h, mod + OFF_BASEDATA))
    out = {}
    for ebd in items:
        if not ebd:
            continue
        mode = i32(h, ebd + 0x10)
        bli = u64(h, ebd + 0x28)
        if not bli:
            continue
        _, L_n, L_items = lst(h, u64(h, bli + 0x88))
        out[mode] = L_items
    return out


def restore(h):
    if not os.path.exists(BACKUP):
        print("X 无备份")
        return 1
    bk = json.load(open(BACKUP, encoding="utf-8"))
    for e in bk["writes"]:
        icall.write_mem(h, e["va"], bytes.fromhex(e["old"]))
        cur = icall.read_mem(h, e["va"], e["size"]).hex()
        print("  restore %#x -> %s %s" % (e["va"], cur, "OK" if cur == e["old"] else "MISMATCH"))
    print("已还原 %d 处" % len(bk["writes"]))
    return 0


def main():
    apply = "--apply" in sys.argv
    do_restore = "--restore" in sys.argv
    h, pid, base = icall.open_game()
    if not h:
        print("X")
        return 1
    try:
        print("pid=%d  mode=%s\n" % (pid, "APPLY" if apply else ("RESTORE" if do_restore else "DRY-RUN")))
        if do_restore:
            return restore(h)

        layers = get_layers(h, base)
        if 2 not in layers or 3 not in layers:
            print("X 需要迪拉克(Mode=2)和量子(Mode=3)都在准备页")
            return 2

        src = u64(h, layers[2][0] + 0x78)      # 迪拉克 layer0 bossGroup
        dst = u64(h, layers[3][0] + 0x78)      # 量子 layer0 bossGroup
        if not src or not dst:
            print("X bossGroup 指针缺失 src=%#x dst=%#x" % (src, dst))
            return 3

        print("源（迪拉克 layer0 bossGroup=%#x）:" % src)
        print("  groupID=%s InitType=%s bossID=%s uniqueIDList=%#x areaName=%#x lua=%#x"
              % (i32(h, src + 0x14), i32(h, src + 0x1C), i32(h, src + 0x34),
                 u64(h, src + 0x50), u64(h, src + 0x28), u64(h, src + 0x58)))
        print("目标（量子 layer0 bossGroup=%#x）当前:" % dst)
        print("  groupID=%s InitType=%s bossID=%s uniqueIDList=%#x areaName=%#x lua=%#x\n"
              % (i32(h, dst + 0x14), i32(h, dst + 0x1C), i32(h, dst + 0x34),
                 u64(h, dst + 0x50), u64(h, dst + 0x28), u64(h, dst + 0x58)))

        plan = [
            (dst + 0x20, icall.read_mem(h, src + 0x20, 4), "ScoreRatio <- 迪拉克"),
            (dst + 0x1C, icall.read_mem(h, src + 0x1C, 4), "MonsterInitType <- 迪拉克"),
            (dst + 0x34, icall.read_mem(h, src + 0x34, 4), "bossID <- 迪拉克"),
            (dst + 0x50, icall.read_mem(h, src + 0x50, 8), "uniqueIDList <- 迪拉克指针"),
        ]
        # 自愈：若准备页 Refresh 把方案 A 的字段冲掉了，一并补回
        if i32(h, dst + 0x14) != 52:
            print("!! 检测到 bossGroup 被 Refresh 重置，先补回基础字段")
            plan = [
                (dst + 0x14, struct.pack("<i", 52), "groupID = 52（补）"),
                (dst + 0x18, struct.pack("<i", 3600), "maxScore = 3600（补）"),
                (dst + 0x30, struct.pack("<B", 1), "isBoss = 1（补）"),
                (dst + 0x3C, struct.pack("<i", i32(h, layers[3][0] + 0x20) or 1001),
                 "environmentID（补）"),
                (dst + 0x28, icall.read_mem(h, src + 0x28, 8), "areaName <- 迪拉克（补）"),
                (dst + 0x58, icall.read_mem(h, src + 0x58, 8), "luaFilePath <- 迪拉克（补）"),
                (layers[3][0] + 0x68, struct.pack("<i", 52), "_bossGroupID = 52（补）"),
            ] + plan
        print("计划写入 %d 处：" % len(plan))
        writes = []
        for va, data, desc in plan:
            old = icall.read_mem(h, va, len(data))
            print("  %#012x  %-28s  %s -> %s %s"
                  % (va, desc, old.hex(), data.hex(), "(相同)" if old == data else ""))
            writes.append({"va": va, "old": old.hex(), "new": data.hex(), "size": len(data), "desc": desc})

        if not apply:
            print("\n[DRY-RUN] 未写入。加 --apply 执行。")
            return 0

        for e in writes:
            icall.write_mem(h, e["va"], bytes.fromhex(e["new"]))
        json.dump({"pid": pid, "writes": writes}, open(BACKUP, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        print("\n已写入，备份 -> %s" % BACKUP)
        print("回读: groupID=%s InitType=%s bossID=%s uniqueIDList=%#x maxScore=%s isBoss=%s"
              % (i32(h, dst + 0x14), i32(h, dst + 0x1C), i32(h, dst + 0x34),
                 u64(h, dst + 0x50), i32(h, dst + 0x18), icall.read_mem(h, dst + 0x30, 1)[0]))
        print("\n现在直接进 BOSS 关。若又卡住，先看日志：")
        print("  C:\\Users\\Administrator\\AppData\\LocalLow\\miHoYo\\Honkai Impact 3\\output_log.txt")
        return 0
    finally:
        icall.k32.CloseHandle(h)


if __name__ == "__main__":
    sys.exit(main() or 0)
