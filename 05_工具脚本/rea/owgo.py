# -*- coding: utf-8 -*-
"""owgo —— 重启游戏后的一站式检查/调用

把「装信箱 → 抓 this → 预检 → 调用」串起来，避免多次来回。
预检不通过就**不会**调用 GoToOWEndless，所以不会白崩一次。

用法:
    python owgo.py check          # 装信箱 + 抓 this + 预检（安全，可反复跑）
    python owgo.py call           # 预检通过后才真正调 GoToOWEndless
    python owgo.py show           # 只看当前状态，不装不改
"""
import json
import os
import struct
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, ".owgo.json")

RVA_UPDATE = icall.HOST_RVA          # 0x21D2550 信箱宿主
RVA_ONPACKET = 0x189AFD0             # OWEndlessModule.OnPacket  收 this
RVA_GOTO = 0x19C5E00                 # OWEndlessModule.GoToOWEndless
RVA_ACTIVE = 0x3758440               # TwoEndless.GetActiveMode
RVA_CURRENT = 0x18981B0              # OWEndlessModule.GetCurrentEndlessData

OFF_PRE_ACTIVITY = 0x50
OFF_TWO_ENDLESS = 0x58
OFF_BASE_LIST = 0x68
SLOT_THIS = 0x40                     # 捕获槽（避开信箱 0x00~0x3f）

MODE_NAME = {0: "None", 1: "Normal", 2: "Openworld(迪拉克之海)", 3: "Quantum(量子奇点)",
             4: "Ultra(超弦空间)", 5: "Greedy(贪婪)", 6: "Front(前哨)"}


def q(h, va):
    b = icall.read_mem(h, va, 8)
    return struct.unpack("<Q", b)[0] if b and len(b) == 8 else None


def u32(h, va):
    b = icall.read_mem(h, va, 4)
    return struct.unpack("<I", b)[0] if b and len(b) == 4 else None


def i32(h, va):
    b = icall.read_mem(h, va, 4)
    return struct.unpack("<i", b)[0] if b and len(b) == 4 else None


def load():
    if os.path.exists(STATE):
        try:
            return json.load(open(STATE))
        except Exception:
            return None
    return None


def save(d):
    json.dump(d, open(STATE, "w"), indent=2)


def ensure_mailbox(h, pid, base):
    """保证信箱在位；游戏重启过就重装。"""
    st = icall.load_state()
    if st and st.get("pid") == pid:
        cur = icall.read_mem(h, base + RVA_UPDATE, 14)
        if cur and cur[:2] == b"\xFF\x25":
            print("  信箱已在位 %#x（pid %d）" % (st["mailbox"], pid))
            return st
        print("  状态文件在但入口不是钩子 → 重装")
    print("  安装信箱…")
    if icall.cmd_install() != 0:
        return None
    return icall.load_state()


def capture_this(h, pid, base):
    """临时挂 OnPacket 抓 rcx(this)，抓完立刻还原。"""
    print("  抓 OWEndlessModule 实例（临时钩 OnPacket，3 秒）…")
    if icall.cmd_hook(RVA_ONPACKET, SLOT_THIS) != 0:
        return None
    st = icall.load_state()
    slot = st["page"] + SLOT_THIS
    got = 0
    try:
        t0 = time.time()
        while time.time() - t0 < 3.0:
            v = q(h, slot)
            if v:
                got = v
                break
            time.sleep(0.05)
    finally:
        icall.cmd_unhook(RVA_ONPACKET)
    return got or None


def probe(h, st, this, base):
    """只读 + 两个 getter，判断 SetupView 会不会炸。"""
    te = q(h, this + OFF_TWO_ENDLESS)
    lst = q(h, this + OFF_BASE_LIST)
    pre = q(h, this + OFF_PRE_ACTIVITY)
    print("  this=%#x  TwoEndless=%#x  baseDataList=%#x  PreActivity=%#x" % (
        this, te or 0, lst or 0, pre or 0))
    if not te or not lst:
        print("  ✗ 关键字段为空，this 可能不对")
        return None, None, []

    items = q(h, lst + 0x10)
    size = u32(h, lst + 0x18) or 0
    modes = []
    for i in range(size):
        elem = q(h, items + 0x20 + i * 8)
        if elem:
            modes.append(u32(h, elem + 0x10))
    print("  baseDataList 共 %d 条，模式 = %s" % (size, modes))

    mb = st["mailbox"]
    if icall.cmd_call(base + RVA_ACTIVE, [te], 5.0) != 0:
        return None, None, modes
    active = q(h, mb + 0x30)
    print("  GetActiveMode() = %s  %s" % (active, MODE_NAME.get(active, "?")))

    if icall.cmd_call(base + RVA_CURRENT, [this], 5.0) != 0:
        return None, None, modes
    cur = q(h, mb + 0x30)
    print("  GetCurrentEndlessData() = %#x" % (cur or 0))

    # GroupInfo 只有在收到 GetOpenworldEndlessDataRsp 之后才被填。
    # 没填过时 _GroupLevel=0，RefreshPlayerGroup 查表必落空 -> NRE。
    # 客户端 OWEndlessGroup 表里 mode=2 只有 21~24。
    if cur:
        g = q(h, cur + 0x20)
        if g:
            print("  GroupInfo: _GroupID=%s  _GroupLevel=%s  _CurTopGroupLevel=%s  _rsp=%#x"
                  % (u32(h, g + 0x20), i32(h, g + 0x24),
                     u32(h, g + 0x28), q(h, g + 0x18) or 0))
        else:
            print("  GroupInfo = 0（RefreshPlayerGroup 会在 +0xDE 那处判空 NRE）")
    return active, cur, modes


def cmd_check():
    h, pid, base = icall.open_game()
    if not h:
        print("游戏未运行 / 需要管理员权限")
        return 1
    try:
        st = ensure_mailbox(h, pid, base)
        if not st:
            return 1
        d = load() or {}
        this = d.get("this") if d.get("pid") == pid else None
        if this:
            print("  沿用上次抓到的 this=%#x" % this)
        else:
            this = capture_this(h, pid, base)
            if not this:
                print("  ✗ 3 秒内没抓到 this（客户端在收包吗？）")
                return 1
            print("  ✓ this=%#x" % this)
            save({"pid": pid, "base": base, "this": this})

        print("\n预检：")
        active, cur, modes = probe(h, st, this, base)
        print()
        if cur:
            print("✓ 放行：GetCurrentEndlessData 非空，SetupView 不会 NRE")
            print("  下一步： python owgo.py call")
            return 0
        print("✗ 拦截：GetCurrentEndlessData = null")
        if active not in (2, 3):
            print("  GetActiveMode()=%s，baseDataList 只有 %s" % (
                MODE_NAME.get(active, active), modes))
            print("  需要 CurStatus.EndlessType = 2 或 3。")
            print("  服务端已切到 2 的话，说明客户端还没重新拉状态 —— 必须重启客户端登录。")
        else:
            print("  GetActiveMode()=%s 已在列表里，但取到 null —— 逻辑与预期不符" % active)
        return 2
    finally:
        icall.k32.CloseHandle(h)


def cmd_call():
    h, pid, base = icall.open_game()
    if not h:
        print("游戏未运行")
        return 1
    try:
        st = icall.load_state()
        d = load()
        if not st or st.get("pid") != pid:
            print("信箱失效，先跑 python owgo.py check")
            return 1
        if not d or d.get("pid") != pid or not d.get("this"):
            print("还没有 this，先跑 python owgo.py check")
            return 1
        this = d["this"]

        # 调用前再预检一次，不通过绝不调用
        active, cur, modes = probe(h, st, this, base)
        if not cur:
            print("\n✗ 预检未通过，拒绝调用 GoToOWEndless")
            return 2

        print("\n调用 GoToOWEndless(this=%#x) …" % this)
        rc = icall.cmd_call(base + RVA_GOTO, [this], 15.0)
        if rc != 0:
            print("✗ 调用失败")
            return rc
        print("✓ 已返回。预期：加载轮出现后关闭，进入迪拉克界面。")
        print("  若仍黑屏，立刻看服务端日志的 3419 速率（正常应为个位数）。")
        return 0
    finally:
        icall.k32.CloseHandle(h)


def cmd_show():
    h, pid, base = icall.open_game()
    if not h:
        print("游戏未运行")
        return 1
    try:
        st = icall.load_state()
        d = load()
        print("pid=%d  base=%#x" % (pid, base))
        cur = icall.read_mem(h, base + RVA_UPDATE, 14)
        print("Update 入口: %s" % ("已挂钩" if cur and cur[:2] == b"\xFF\x25" else "原始"))
        print("信箱: %s" % (("在位 %#x" % st["mailbox"]) if st and st.get("pid") == pid else "无/失效"))
        this = d.get("this") if d and d.get("pid") == pid else None
        print("this: %s" % (("%#x" % this) if this else "未抓"))
        if this and st and st.get("pid") == pid:
            probe(h, st, this, base)
    finally:
        icall.k32.CloseHandle(h)
    return 0


def main():
    a = sys.argv[1:] or ["check"]
    cmd = a[0].lower()
    if cmd == "check":
        return cmd_check()
    if cmd == "call":
        return cmd_call()
    if cmd == "show":
        return cmd_show()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
