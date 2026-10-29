# -*- coding: utf-8 -*-
"""probe_group —— 只读探测 OWEndlessGroup 配置表到底有哪些行

为什么需要它
------------
第二次黑屏的 NRE 抛在 MonoOWEndlessUIManager.RefreshPlayerGroup+0x404：

    ebx  = GroupInfo._GroupLevel              ; GroupInfo+0x24
    meta = GetOWEndlessGroupMetaByKey(ebx)    ; 内部 = (ebx, GetActiveMode())
    if (meta == null) -> NRE

也就是说 (GroupLevel, EndlessType) 这个二元 key 在 Excel 表里查不到。
本脚本把整张表的 key 空间扫一遍，得出「哪些 (level, mode) 有行」，
从而反推服务端该下发什么 GroupLevel。

安全性
------
只调用三类东西：
  1. GetCurrentEndlessData(this)      —— 纯 getter
  2. GetTopGroupLevel() / GetTopLevelPlayerGroup() / GetGroupCountByGroupLevel(n)
  3. GetOWEndlessGroupMetaByKey(level, mode) —— 纯字典查询
不改任何游戏状态，不触发 UI 装配，不写业务字段。

用法:
    python probe_group.py           # 全量扫描（纯观察）
    python probe_group.py 12        # 只扫 level 1..12
    python probe_group.py 25 --load # 先手动触发 LoadFromFileAndBuildMap() 再扫
"""
import contextlib
import io
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall   # noqa: E402
import owgo    # noqa: E402

RVA_ACTIVE      = 0x3758440    # TwoEndless.GetActiveMode() -> EndlessMode
RVA_CURRENT     = 0x18981B0    # OWEndlessModule.GetCurrentEndlessData()
RVA_GROUP_BY_KEY = 0x35062C0   # GetOWEndlessGroupMetaByKey(int GroupLevel, EndlessMode mode)
RVA_TOP_LEVEL   = 0x3506300    # GetTopGroupLevel() -> int
RVA_TOP_PGROUP  = 0x35063A0    # GetTopLevelPlayerGroup() -> int
RVA_GROUP_COUNT = 0x3506030    # GetGroupCountByGroupLevel(int level) -> int
RVA_LOAD_TABLE  = 0x3506600    # LoadFromFileAndBuildMap() -> void（会改状态，需 --load）

OFF_DATA_GROUP  = 0x20         # EndlessBaseData.<Group>   (GroupInfo*)
OFF_GROUP_RSP   = 0x18         # GroupInfo._rsp
OFF_GROUP_ID    = 0x20         # GroupInfo._GroupID
OFF_GROUP_LEVEL = 0x24         # GroupInfo._GroupLevel   ← 喂给查询的那个
OFF_GROUP_TOP   = 0x28         # GroupInfo._CurTopGroupLevel
OFF_GROUP_TOPN  = 0x2C         # GroupInfo._TopGroupPlayerNum


def q(h, va):
    b = icall.read_mem(h, va, 8)
    return struct.unpack("<Q", b)[0] if b and len(b) == 8 else None


def u32(h, va):
    b = icall.read_mem(h, va, 4)
    return struct.unpack("<I", b)[0] if b and len(b) == 4 else None


def i32(h, va):
    b = icall.read_mem(h, va, 4)
    return struct.unpack("<i", b)[0] if b and len(b) == 4 else None


def call(h, mb, va, args, wait=5.0):
    """静默投递，返回 (rc, rax)。"""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = icall.cmd_call(va, args, wait)
    if rc != 0:
        return rc, None
    return 0, q(h, mb + 0x30)


def main():
    argv = sys.argv[1:]
    do_load = "--load" in argv
    skip_count = "--skip-count" in argv
    modes = [2, 3, 4]
    for a in argv:
        if a.startswith("--modes="):
            modes = [int(x) for x in a.split("=", 1)[1].split(",")]
    nums = [a for a in argv if not a.startswith("-")]
    limit = int(nums[0]) if nums else 25

    h, pid, base = icall.open_game()
    if not h:
        print("游戏未运行 / 需要管理员权限")
        return 1
    try:
        st = owgo.ensure_mailbox(h, pid, base)
        if not st:
            return 1
        mb = st["mailbox"]

        d = owgo.load() or {}
        this = d.get("this") if d.get("pid") == pid else None
        if not this:
            print("还没有 this，先跑 python owgo.py check")
            return 1
        print("  pid=%d  base=%#x  this=%#x" % (pid, base, this))

        # ---- 1. 当前生效模式 ----
        te = q(h, this + owgo.OFF_TWO_ENDLESS)
        if not te:
            print("✗ TwoEndless 字段为空，this 可能不对")
            return 1
        rc, active = call(h, mb, base + RVA_ACTIVE, [te])
        if rc != 0 or active is None:
            print("✗ GetActiveMode 调用失败")
            return 1
        active &= 0xFF
        print("  GetActiveMode() = %d  %s" % (active, owgo.MODE_NAME.get(active, "?")))

        # ---- 2. 当前 EndlessData -> GroupInfo ----
        rc, data = call(h, mb, base + RVA_CURRENT, [this])
        if rc != 0 or not data:
            print("✗ GetCurrentEndlessData() = null，先修模式再谈分组")
            return 2
        group = q(h, data + OFF_DATA_GROUP)
        print("  EndlessBaseData = %#x  .Group = %#x" % (data, group or 0))
        if not group:
            print("✗ Group 为空，NRE 会先炸在 +0xDE 那处判空")
            return 2
        gid = u32(h, group + OFF_GROUP_ID)
        glv = i32(h, group + OFF_GROUP_LEVEL)
        gtop = u32(h, group + OFF_GROUP_TOP)
        gtopn = u32(h, group + OFF_GROUP_TOPN)
        rsp = q(h, group + OFF_GROUP_RSP)
        print("  GroupInfo: _GroupID=%s  _GroupLevel=%s  _CurTopGroupLevel=%s  _TopGroupPlayerNum=%s  _rsp=%#x"
              % (gid, glv, gtop, gtopn, rsp or 0))
        print("  → 客户端实际拿去查表的是 _GroupLevel = %s" % glv)

        # ---- 3. 表级只读接口 ----
        def table_stats(tag):
            rc, top = call(h, mb, base + RVA_TOP_LEVEL, [])
            rc2, tpg = call(h, mb, base + RVA_TOP_PGROUP, [])
            print("  [%s] GetTopGroupLevel()      = %s%s"
                  % (tag, top, "  ← 0 说明表没加载" if top == 0 else ""))
            print("  [%s] GetTopLevelPlayerGroup()= %s" % (tag, tpg))
            return top, tpg

        print("\n表级接口：")
        top, tpg = table_stats("加载前")

        # 只有显式 --load 才动状态。LoadFromFileAndBuildMap 内部会去读资源文件，
        # 若资源缺失可能抛异常，而异常会顺着钩子冒进 Update，所以默认不碰。
        if do_load:
            print("\n手动触发 LoadFromFileAndBuildMap() …")
            rc, _ = call(h, mb, base + RVA_LOAD_TABLE, [], wait=15.0)
            print("  返回 rc=%d（void 函数，rax 无意义）" % rc)
            table_stats("加载后")

        # ---- 4. 逐 level 扫 ----
        print("\n逐 GroupLevel 扫描（1..%d），modes=%s：" % (limit, modes))
        hdr = "  %-6s" % "level"
        if not skip_count:
            hdr += " %-8s" % "count"
        for m in modes:
            hdr += " %-12s" % ("meta(m=%d)" % m)
        print(hdr)
        rows = []
        for lv in range(1, limit + 1):
            cnt = None
            if not skip_count:
                rc, cnt = call(h, mb, base + RVA_GROUP_COUNT, [lv])
                if rc != 0:
                    cnt = None
            metas = {}
            for m in modes:
                rc, mv = call(h, mb, base + RVA_GROUP_BY_KEY, [lv, m])
                metas[m] = mv if rc == 0 else None
            rows.append((lv, cnt, metas))
            line = "  %-6d" % lv
            if not skip_count:
                line += " %-8s" % (cnt if cnt is not None else "-")
            for m in modes:
                v = metas[m]
                line += " %-12s" % (("%#x" % v) if v else "null")
            if any(metas.values()):
                line += "  ★"
            print(line)

        # ---- 5. 结论 ----
        print("\n结论：")
        for m in modes:
            ok = [r[0] for r in rows if r[2].get(m)]
            print("  mode=%d 有行的 level: %s" % (m, ok if ok else "无"))
        mine = [r[2].get(active) for r in rows if r[0] == glv]
        cur_ok = bool(mine and mine[0])
        if cur_ok:
            print("  ✓ 当前 _GroupLevel=%s 在 mode=%d 里有行 —— 查表不是阻塞点" % (glv, active))
        else:
            ok = [r[0] for r in rows if r[2].get(active)]
            print("  ✗ 当前 _GroupLevel=%s 在 mode=%d 下查不到" % (glv, active))
            if ok:
                print("    修法：让服务端 GetOpenworldEndlessDataRsp.GroupLevel = %s" % ok[0])
            else:
                print("    mode=%d 整段为空 —— 这条路走不通" % active)
        return 0
    finally:
        icall.k32.CloseHandle(h)


if __name__ == "__main__":
    sys.exit(main())
