# -*- coding: utf-8 -*-
"""gotoow —— GoToOWEndless 四步实验（常驻指令槽版）

前置事实（全部来自 rea/_rea 的反编译与符号表，非推测）
----------------------------------------------------
| 符号 | RVA | 说明 |
|---|---|---|
| `MonoClientPacketConsumer.Update` | 0x21D2550 | icall 的宿主，钩子只打这一次 |
| `OWEndlessModule.OnGetOpenworldEndlessDataRsp` | 0x189A7D0 | bool(proto.GetOpenworldEndlessDataRsp)，实例方法 → rcx = this |
| `OWEndlessModule.GoToOWEndless` | 0x19C5E00 | void()，实例方法 → rcx = this |

GoToOWEndless 的真实行为（`bodies_merged.tsv` @1819C5E00）：

    if (!IsPatched(0x108d7)) {
        ctx = new LoadingWheelWidgetForTwoRspContext(0xd5c, 0xd7c, null);
        ctx.SetIgnoreMaxWaitTimeForReq(0xd5b);
        ctx->cmdCallBack = new KeyGeneratedEventHandler(this, <回调>);
        MainUIManager::ShowWidget(mainUI, ctx, 0);
        RequestOWEndlessData(...);        // 发 3419
    }

    0xd5c = 3420 GetOpenworldEndlessDataRsp   ← 服务端会回
    0xd7c = 3452 EndlessInSettleNotify        ← 服务端不发，但不需要
    0xd5b = 3419 GetOpenworldEndlessDataReq

两个 waitCmd 是 OR 不是 AND（OnPacket @0x180915860 实测）：
命中任意一个就 Finish()。所以 3420 到达即可关轮，无需补发 3452。
但 SetIgnoreMaxWaitTimeForReq 把 5 秒兜底关掉了 —— 3420 不来就永远转。

注意：`object_new` 不返回 null，反编译里那个 `if (this_01 == 0)` 是死代码。
真正会空引用的是 `MainUIManager` / `NetworkManager` 单例 —— 所以必须在
**主界面、世界地图能打开**的状态下调用，不能在加载画面里调。

四步
----
    1  install     在 Update 入口挂常驻信箱
    2  hook        挂 OnGetOpenworldEndlessDataRsp，捕获 rcx(this)
    3  watch       等 this 出现（此时去游戏里：世界地图 → 出击 → 开放世界）
    4  call        GoToOWEndless(this)

用法
----
    python gotoow.py diag               # 看全入口/信箱/捕获槽/钩子四处状态（先跑这个）
    python gotoow.py 1
    python gotoow.py probe --seconds 15 # 盯信箱，必须「0 次变化」才继续
    python gotoow.py 2
    python gotoow.py 3 --timeout 180      # 挂着等，期间去点开放世界
    python gotoow.py 4
    python gotoow.py all                  # 1→2→3→4，中途停在 3 等你操作
    python gotoow.py revert               # 撤钩子 + 还原入口
"""
import os
import struct
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402  同目录的 icall.py

RVA_UPDATE = icall.HOST_RVA            # 0x21D2550 MonoClientPacketConsumer.Update
RVA_RSP = 0x189A7D0                    # OWEndlessModule.OnGetOpenworldEndlessDataRsp
RVA_GOTO = 0x19C5E00                   # OWEndlessModule.GoToOWEndless
CAPTURE_SLOT = icall.CAPTURE_OFF       # 0x38

TAG = "[gotoow]"


def _state():
    return icall.load_state()


def cmd_status():
    st = _state()
    pid = icall.find_pid()
    if not pid:
        print("%s 游戏未运行（BH3.exe）" % TAG)
        return 1
    h, pid, base = icall.open_game()
    if not h:
        print("%s OpenProcess 失败（需要管理员权限？）" % TAG)
        return 1
    try:
        cur = icall.read_mem(h, base + RVA_UPDATE, 14)
        hooked = bool(cur) and cur[:2] == b"\xFF\x25"
        print("%s PID=%d  基址=%#x" % (TAG, pid, base))
        print("  Update 入口 [%s] %s" % (
            cur.hex(" ") if cur else "?",
            "已挂钩子" if hooked else ("原始" if cur == icall.orig_bytes() else "未知/被改")))
        if not st:
            print("  信箱：未安装")
            return 0
        alive = st.get("pid") == pid
        print("  信箱 %#x %s" % (st.get("mailbox", 0), "有效" if alive else "失效（游戏重启过）"))
        hooks = st.get("hooks", {})
        if hooks:
            for k, v in hooks.items():
                print("  钩子 RVA %s → 捕获槽 %#x" % (k, v["slot"]))
        else:
            print("  钩子：无")
        if alive:
            raw = icall.read_mem(h, st["page"] + CAPTURE_SLOT, 8)
            if raw and len(raw) == 8:
                this_val = struct.unpack("<Q", raw)[0]
                print("  捕获槽(this) = %s" % (("%#x" % this_val) if this_val else "空"))
    finally:
        icall.k32.CloseHandle(h)
    return 0


def cmd_step1():
    print("%s ① install —— 在 Update(%#x) 挂常驻信箱" % (TAG, RVA_UPDATE))
    return icall.cmd_install()


def cmd_step2():
    st = _state()
    if not st:
        print("%s 还没 install，先跑 step 1" % TAG)
        return 1
    key = str(RVA_RSP)
    if key in (st.get("hooks") or {}):
        print("%s ② 已挂钩，跳过（槽 %#x）" % (TAG, st["hooks"][key]["slot"]))
        return 0
    print("%s ② hook —— OnGetOpenworldEndlessDataRsp(%#x)，捕获 rcx(this)" % (TAG, RVA_RSP))
    return icall.cmd_hook(RVA_RSP, CAPTURE_SLOT)


def _read_this(h, st):
    raw = icall.read_mem(h, st["page"] + CAPTURE_SLOT, 8)
    if not raw or len(raw) != 8:
        return None
    return struct.unpack("<Q", raw)[0]


def cmd_step3(timeout=180):
    st = _state()
    if not st:
        print("%s 还没 install" % TAG)
        return 1
    h, pid, base = icall.open_game()
    if not h:
        return 1
    if st.get("pid") != pid:
        print("%s 信箱失效（游戏重启过），重跑 step 1" % TAG)
        icall.k32.CloseHandle(h)
        return 1
    print("%s ③ 等 this —— 现在去游戏里：主界面 → 世界地图 → 出击页签 → 开放世界按钮" % TAG)
    print("      （这一步会触发 GetOpenworldEndlessDataReq(3419)，服务端回 3420，钩子就抓到 this）")
    t0 = time.time()
    try:
        while time.time() - t0 < timeout:
            v = _read_this(h, st)
            if v:
                print("%s ✓ 捕获到 this = %#x  （耗时 %.1fs）" % (TAG, v, time.time() - t0))
                # 粗校验：对象头应是合法指针
                klass = icall.read_mem(h, v, 8)
                if klass:
                    kva = struct.unpack("<Q", klass)[0]
                    print("    [this] = %#x （klass 指针）" % kva)
                    if kva < 0x10000:
                        print("    ⚠ klass 指针不像有效值，谨慎往下走")
                return 0
            time.sleep(0.3)
    finally:
        icall.k32.CloseHandle(h)
    print("%s ✗ %.0fs 内没抓到 this。检查：是否真的进了开放世界按钮；服务端有没有打印 [Abyss] GetOpenworldEndlessDataReq" % (TAG, timeout))
    return 1


def cmd_step4(wait=10.0):
    st = _state()
    if not st:
        print("%s 还没 install" % TAG)
        return 1
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        this_val = _read_this(h, st)
    finally:
        icall.k32.CloseHandle(h)
    if not this_val:
        print("%s 捕获槽是空的，先跑 step 3" % TAG)
        return 1
    print("%s ④ call —— GoToOWEndless(%#x)，this=%#x" % (TAG, base + RVA_GOTO, this_val))
    print("    预期：出现加载轮（等 3420 与 3452），随后进入迪拉克界面")
    print("    若加载轮一直转 → 卡在 3452 EndlessInSettleNotify（服务端不发这个包）")
    return icall.cmd_call(base + RVA_GOTO, [this_val], wait)


def cmd_revert():
    st = _state()
    if not st:
        print("%s 没装过" % TAG)
        return 0
    rc = 0
    if st.get("hooks"):
        rc |= icall.cmd_unhook()
    rc |= icall.cmd_uninstall()
    return rc


def cmd_probe(seconds=10.0):
    """盯信箱：看有没有「不是我们写的」字节冒出来。

    2026-10-25 15:17 那次崩溃，信箱 pending 被写成非 0、target 为 0，
    导致 stub call 0 直接崩游戏。这个命令用来验证「那块内存会不会自己变」。
    """
    st = _state()
    if not st:
        print("%s 还没 install，先跑 step 1" % TAG)
        return 1
    h, pid, base = icall.open_game()
    if not h:
        return 1
    if st.get("pid") != pid:
        print("%s 信箱失效（游戏重启过），重跑 step 1" % TAG)
        icall.k32.CloseHandle(h)
        return 1
    mb = st["mailbox"]
    print("%s 盯 %#x 共 %.0fs（每 0.2s 采一次，只报变化）" % (TAG, mb, seconds))
    prev = icall.read_mem(h, mb, 0x40)
    print("  初始: %s" % (prev.hex(" ") if prev else "读取失败"))
    t0 = time.time()
    changes = 0
    try:
        while time.time() - t0 < seconds:
            cur = icall.read_mem(h, mb, 0x40)
            if cur != prev:
                changes += 1
                diff = [i for i in range(min(len(cur or b""), len(prev or b"")))
                        if cur[i] != prev[i]]
                print("  [%5.2fs] 变化 @%s : %s → %s" % (
                    time.time() - t0,
                    ",".join("+%#x" % i for i in diff),
                    " ".join("%02x" % prev[i] for i in diff),
                    " ".join("%02x" % cur[i] for i in diff)))
                prev = cur
            time.sleep(0.2)
    finally:
        icall.k32.CloseHandle(h)
    print("%s 采样结束：%d 次变化 %s" % (
        TAG, changes, "（有外部写入！）" if changes else "（安静，说明上次是偶发）"))
    return 0


def cmd_diag():
    """一次性看全四处状态：Update 入口 / 信箱 / 捕获槽 / 钩子。

    重跑实验前先跑这个。任何一处不对，都不要往下走。
    """
    st = _state()
    pid = icall.find_pid()
    if not pid:
        print("%s 游戏未运行（BH3.exe）—— 先启动游戏到主界面" % TAG)
        return 1
    h, pid, base = icall.open_game()
    if not h:
        print("%s OpenProcess 失败（需要管理员权限）" % TAG)
        return 1
    bad = []
    try:
        print("%s === 环境 ===  PID=%d  基址=%#x" % (TAG, pid, base))

        cur = icall.read_mem(h, base + RVA_UPDATE, 14)
        orig = icall.orig_bytes()
        if not cur:
            print("  ✗ Update 入口读取失败"); bad.append("入口不可读")
        elif cur == orig:
            print("  · Update 入口：原始 [%s]" % cur.hex(" "))
        elif cur[:2] == b"\xFF\x25":
            tgt = struct.unpack("<Q", cur[6:])[0]
            print("  · Update 入口：已挂钩 → %#x" % tgt)
        else:
            print("  ✗ Update 入口：未知字节 [%s]" % cur.hex(" ")); bad.append("入口被改")

        if not st:
            print("  · 信箱：未安装")
            return 0
        if st.get("pid") != pid:
            print("  ✗ 信箱状态来自旧进程（pid %s ≠ %d）→ 必须重跑 step 1" % (st.get("pid"), pid))
            return 1

        mb = st["mailbox"]
        raw = icall.read_mem(h, mb, 0x40)
        if not raw:
            print("  ✗ 信箱读取失败"); bad.append("信箱不可读")
        else:
            print("  · 信箱 %#x" % mb)
            for i in range(0, 0x40, 16):
                print("      +%02x  %s" % (i, raw[i:i + 16].hex(" ")))
            pend, done = raw[0], raw[1]
            tgt = struct.unpack("<Q", raw[8:16])[0]
            print("      pending=%#04x  done=%d  target=%#x" % (pend, done, tgt))
            if pend not in (0, icall.MAGIC):
                print("      ✗ pending 是非魔数的脏值 —— 就是上次崩溃的形态")
                bad.append("pending 脏")
            if pend == icall.MAGIC:
                print("      ⚠ pending 还挂着一条未取走的命令")

        slot = icall.read_mem(h, st["page"] + CAPTURE_SLOT, 8)
        this_val = struct.unpack("<Q", slot)[0] if slot and len(slot) == 8 else 0
        print("  · 捕获槽 %#x = %s" % (st["page"] + CAPTURE_SLOT,
                                      ("%#x" % this_val) if this_val else "空"))

        hooks = st.get("hooks") or {}
        if not hooks:
            print("  · 钩子：无（step 2 还没跑）")
        for k, v in hooks.items():
            rva = int(k)
            cur2 = icall.read_mem(h, base + rva, 6)
            landed = bool(cur2) and cur2[:2] == b"\xFF\x25"
            print("  %s 钩子 RVA %#x → 槽 %#x  %s" % (
                "·" if landed else "✗", rva, v["slot"], "在位" if landed else "入口已不在（被还原/被覆盖）"))
            if not landed:
                bad.append("钩子 %#x 丢失" % rva)
    finally:
        icall.k32.CloseHandle(h)

    print()
    if bad:
        print("%s 结论：有 %d 处异常 → %s" % (TAG, len(bad), "；".join(bad)))
        print("       先 revert，再按 1 → probe → 2 → 3 → 4 重来")
        return 1
    print("%s 结论：四处状态一致，可以继续" % TAG)
    return 0


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    step = args[0].lower()
    if step == "status":
        return cmd_status()
    if step in ("diag", "d"):
        return cmd_diag()
    if step in ("1", "install"):
        return cmd_step1()
    if step in ("2", "hook"):
        return cmd_step2()
    if step in ("3", "watch"):
        t = 180
        if "--timeout" in args:
            t = int(args[args.index("--timeout") + 1])
        return cmd_step3(t)
    if step in ("4", "call"):
        w = 10.0
        if "--wait" in args:
            w = float(args[args.index("--wait") + 1])
        return cmd_step4(w)
    if step == "probe":
        s = 10.0
        if "--seconds" in args:
            s = float(args[args.index("--seconds") + 1])
        return cmd_probe(s)
    if step == "all":
        for fn in (cmd_step1, cmd_step2, cmd_step3):
            rc = fn()
            if rc:
                return rc
        return cmd_step4()
    if step in ("revert", "uninstall"):
        return cmd_revert()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
