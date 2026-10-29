# -*- coding: utf-8 -*-
"""precheck_ow —— 调 GoToOWEndless 之前的放行检查

SetupView 在 RequestOWEndlessData 之后有两处硬空引用：

    pEVar7 = OWEndlessModule::GetCurrentEndlessData(this);
    if (pEVar7 == NULL) raise_null_reference_exception();   // 0x18185B0A2
    this_00 = pEVar7->DataMode;
    if (this_00 == NULL) raise_null_reference_exception();  // 0x18185B0A8

GetCurrentEndlessData 用 TwoEndless.GetActiveMode() 去 baseDataList 里找匹配项，
找不到就返回 null。所以只要先算一遍「能不能找到」，就能预知 SetupView 会不会炸，
而不是靠调一次 GoToOWEndless 拿游戏去赌。

baseDataList 是固定的两条（TwoEndless = 迪拉克之海 Openworld + 量子奇点 Quantum），
所以 GetActiveMode 必须是 2 或 3 才放行。

用法:
    python precheck_ow.py 0x700ee375dd0
"""
import struct
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402

RVA_GET_ACTIVE_MODE = 0x3758440      # TwoEndless.GetActiveMode
RVA_GET_CURRENT = 0x18981B0          # OWEndlessModule.GetCurrentEndlessData
OFF_TWO_ENDLESS = 0x58
OFF_BASE_LIST = 0x68

MODE_NAME = {0: "None", 1: "Normal", 2: "Openworld(迪拉克之海)", 3: "Quantum(量子奇点)",
             4: "Ultra(超弦空间)", 5: "Greedy(贪婪)", 6: "Front(前哨)"}


def q(h, va):
    b = icall.read_mem(h, va, 8)
    return struct.unpack("<Q", b)[0] if b and len(b) == 8 else None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    this = int(sys.argv[1], 0)
    st = icall.load_state()
    if not st:
        print("还没 install（先 gotoow.py 1）")
        return 1
    h, pid, base = icall.open_game()
    if not h:
        print("游戏未运行")
        return 1
    try:
        if st.get("pid") != pid:
            print("信箱失效（游戏重启过），先重跑 gotoow.py 1")
            return 1

        te = q(h, this + OFF_TWO_ENDLESS)
        lst = q(h, this + OFF_BASE_LIST)
        print("this=%#x  TwoEndless=%#x  baseDataList=%#x" % (this, te or 0, lst or 0))
        if not te or not lst:
            print("✗ 字段为空，this 可能不对")
            return 1

        # 先把列表里的模式读出来（只读，不调用）
        items = q(h, lst + 0x10)
        raw = icall.read_mem(h, lst + 0x18, 4)
        size = struct.unpack("<I", raw)[0] if raw else -1
        modes = []
        for i in range(max(size, 0)):
            elem = q(h, items + 0x20 + i * 8)
            if not elem:
                continue
            m = icall.read_mem(h, elem + 0x10, 4)
            modes.append(struct.unpack("<I", m)[0] if m else -1)
        print("baseDataList 共 %d 条，模式 = %s" % (size, modes))

        # 再问 GetActiveMode 要当前激活模式
        print("\n调用 TwoEndless.GetActiveMode(%#x) …" % te)
        if icall.cmd_call(base + RVA_GET_ACTIVE_MODE, [te], 5.0) != 0:
            print("✗ 调用失败")
            return 1
        raw = icall.read_mem(h, st["mailbox"] + 0x30, 8)
        active = struct.unpack("<Q", raw)[0] & 0xFFFFFFFF if raw else 0
        print("  GetActiveMode() = %d  %s" % (active, MODE_NAME.get(active, "?")))

        print("\n调用 OWEndlessModule.GetCurrentEndlessData(%#x) …" % this)
        if icall.cmd_call(base + RVA_GET_CURRENT, [this], 5.0) != 0:
            print("✗ 调用失败")
            return 1
        raw = icall.read_mem(h, st["mailbox"] + 0x30, 8)
        cur = struct.unpack("<Q", raw)[0] if raw else 0
        print("  GetCurrentEndlessData() = %#x" % cur)

        print()
        if cur:
            print("✓ 放行：SetupView 里那个判空不会炸，可以调 GoToOWEndless")
            return 0
        print("✗ 拦截：返回 null → SetupView 必抛 NRE → 每帧重试 → 3419 风暴")
        if active in (2, 3):
            print("  GetActiveMode 已经是 %d，但列表里没有它 —— 列表内容和预期不符" % active)
        else:
            print("  原因：GetActiveMode()=%d，而 baseDataList 只有 %s" % (active, modes))
            print("  修法：让 CurStatus.EndlessType 变成 2 或 3，"
                  "游戏内聊天打 `abyss legacy 2`（热生效）")
        return 2
    finally:
        icall.k32.CloseHandle(h)


if __name__ == "__main__":
    sys.exit(main())
