# -*- coding: utf-8 -*-
"""wmready —— 等「挑战面板装配好」，然后自动跑 setup

2026-10-25 18:0x 修订：删掉「门禁②：GroupId != 0」
---------------------------------------------------
原来的门禁是：
  ① MGR_SLOT 非 0
  ② get_Group().GroupId != 0

这个 ② 是个**死循环**，直接导致 17:53 那次「卡片未修改成功」：
  装接线 → 才能点卡进迪拉克 → 进去之后 Group 才会被填 → ② 才成立
  也就是说 ② 成立的前提，正是「接线已经装好了」。

证据（本轮现场取证）
  get_Group 反汇编（RVA 0x189DC90）：
        call 0x1818981b0          ; 取 data
        test rax, rax
        je   ...                  ; data 为 null 才返回 0
        mov  rax, [rax + 0x20]    ; return data->Group
        ret
  ——**没有任何 new**，说明它不是「懒创建」，而是读一个已经存在的对象。
  而 17:32「完全正常」那次读到 GroupId=1 / Level=21 / CurTop=22，
  是在**用户已经进入迪拉克之后**读的；17:57 重启后没进过模式，读到 0 是正常的。

  所以 GroupId==0 只说明「还没进过模式」，**不能**说明「客户端拒绝了数据」。

现在改成：
  硬门禁 ① MGR_SLOT 非 0 —— 挑战面板装配完成（卡片对象已存在，setup 才找得到卡）
  信息项 ② Group 状态 —— 打印出来，全零时给一句提示，但**照装不误**

真正防黑屏的防线在服务端：handler 里的 ClientSafeLevels 白名单 + 默认 21。
GroupLevel=35 会 NRE 黑屏那个坑，已经在服务端堵住了，不需要客户端门禁再堵一次。

用法
----
    python wmready.py            最多等 600 秒，就绪后自动 setup --yes
    python wmready.py 300        自定义超时
    python wmready.py 300 --dry  只检测，不装接线
    python wmready.py --force    不等门禁，直接装（面板已开时可省时间）

安全：检测阶段只读；就绪后执行的就是 setup（解锁补丁 + 点击接线）。
"""
import os
import struct
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402
import wmpick as W  # noqa: E402

RVA_GET_MODULE = 0x1A92080   # MonoWorldMapEndlessEntry.get_module
RVA_GET_GROUP = 0x189DC90    # OWEndlessModule.get_Group


def _probe(h, base, st):
    """返回 (mgr, module, group_dict)。

    mgr 非 0 = 挑战面板已装配（这是唯一的硬门禁）。
    group_dict 为 None 或 group_id==0 都只当信息看，不阻塞。
    """
    raw = icall.read_mem(h, st["page"] + W.MGR_SLOT, 8)
    mgr = struct.unpack("<Q", raw)[0] if raw and len(raw) == 8 else 0
    if not mgr:
        return 0, 0, None

    # 取模块实例（静态 getter，传 rcx=0 即可）
    if icall.cmd_call(base + RVA_GET_MODULE, [0], 5.0) != 0:
        return mgr, 0, None
    raw = icall.read_mem(h, st["mailbox"] + 0x30, 8)
    mod = struct.unpack("<Q", raw)[0] if raw and len(raw) == 8 else 0
    if not mod:
        return mgr, 0, None

    if icall.cmd_call(base + RVA_GET_GROUP, [mod], 5.0) != 0:
        return mgr, mod, None
    raw = icall.read_mem(h, st["mailbox"] + 0x30, 8)
    g = struct.unpack("<Q", raw)[0] if raw and len(raw) == 8 else 0
    if not g:
        return mgr, mod, None

    return mgr, mod, {
        "va": g,
        "group_id": W.i32(h, g + 0x20),
        "group_level": W.i32(h, g + 0x24),
        "cur_top": W.i32(h, g + 0x28),
    }


def wait_panel(timeout=600.0):
    """只等硬门禁：挑战面板装配完成。"""
    deadline = time.time() + timeout
    last_note = ""
    while time.time() < deadline:
        h, pid, base = icall.open_game()
        if not h:
            print("\n✗ 找不到游戏进程")
            return None
        try:
            st = icall.load_state()
            if not st or st.get("pid") != pid:
                print("\n✗ 信箱与当前进程不匹配，先跑 python wmpick.py arm")
                return None
            mgr, mod, g = _probe(h, base, st)
        finally:
            icall.k32.CloseHandle(h)

        if mgr:
            print("\n✓ 挑战面板已装配")
            print("  管理器   = %#x" % mgr)
            print("  模块     = %#x" % (mod or 0))
            if g and g["group_id"]:
                print("  Group    = %#x  GroupId=%s GroupLevel=%s CurTop=%s"
                      % (g["va"], g["group_id"], g["group_level"], g["cur_top"]))
                print("  → 分组数据已就绪（说明这一局已经进过迪拉克）")
            elif g:
                print("  Group    = %#x  GroupId=0 GroupLevel=0 CurTop=0" % g["va"])
                print("  → 分组数据还没填。**这是正常的**：Group 只在你真正进入")
                print("    迪拉克之后才会被填。本次照常安装接线，装完点卡进去即可。")
            else:
                print("  Group    = 取不到（模块还没建），照常安装接线")
            return (mgr, mod, g)

        note = "等待挑战面板装配（请在游戏里打开「世界地图 -> 挑战」）"
        if note != last_note:
            sys.stdout.write("\n  … %s" % note)
            sys.stdout.flush()
            last_note = note
        else:
            sys.stdout.write(".")
            sys.stdout.flush()
        time.sleep(1.0)

    print("\n✗ 超时（%.0fs）：挑战面板一直没装配" % timeout)
    return None


def main():
    timeout = 600.0
    dry = "--dry" in sys.argv
    force = "--force" in sys.argv
    for a in sys.argv[1:]:
        try:
            timeout = float(a)
        except ValueError:
            pass

    if force:
        print("--force：跳过门禁，直接安装")
    else:
        print("请打开「世界地图 -> 挑战」面板（最多等 %.0fs）…" % timeout)
        print("  硬门禁：挑战面板装配完成（管理器实例抓到）")
        print("  分组数据只作参考，全零也会照常安装")
        if not wait_panel(timeout):
            print("  提示：面板开过之后如果还是抓不到管理器，先在游戏里把挑战面板")
            print("        关掉再打开一次；确认 wmpick.py arm 装信箱时的 PID 与当前一致。")
            return 1
        if dry:
            print("\n（--dry：只检测，未安装接线）")
            return 0
        time.sleep(0.5)

    if "--yes" not in sys.argv:
        sys.argv.append("--yes")
    print("\n--- 开始安装（解锁补丁 + 点击接线）---")
    return W.cmd_setup()


if __name__ == "__main__":
    sys.exit(main())
