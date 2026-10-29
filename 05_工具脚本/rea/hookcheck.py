# -*- coding: utf-8 -*-
"""hookcheck —— 只读体检：现在的客户端到底有没有被 hook / 有没有残留

背景
----
rehook*.bat / wmpick.py / wmabysspick.py 全部只做 WriteProcessMemory，
不落盘、不写注册表、不挂自启。所以「重启后还在」这件事，只有三种可能：

  1) 启动以后又有人（或某个等待中的脚本）装过一遍  -> 看 rehook*log.txt 时间
  2) 判断依据是旧状态文件（.icall.json 里记的 pid 早就退出了）-> 看第 5 段
  3) 根本不是 hook，是原生数据 / 服务端下发

本脚本把这四件事一次性摆出来，全程只读：

    python rea/_rea/hookcheck.py

退出码：0 = 干净，1 = 发现内存补丁，2 = 游戏没开
"""
import os
import sys
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402

# 所有会被 rehook / wmpick / wmabysspick 碰到的入口
POINTS = [
    ("DoClickAction",                     0x2CFB880, "点击接线（stub -> 信箱）"),
    ("set_ContainerData",                 0x0BFD610, "卡片捕获环形钩子"),
    ("MonoWorldMapUIManager.SetupAllEntry", 0x2D08310, "管理器捕获钩子"),
    ("TypeToMode",                        0x19C6C90, "18 字节补丁：type 0 -> mode 2"),
    ("GoToOWEndless",                     0x19C5E00, "跳转入口（一般不改）"),
    ("OnGetOWEndlessRspForGotoEndless",   0x19C64E0, "回包分流（一般不改）"),
]

STATE_FILES = [
    ("hook 状态", os.path.join(os.path.dirname(os.path.abspath(__file__)), ".icall.json")),
    ("卡片状态", os.path.join(os.path.dirname(os.path.abspath(__file__)), ".wmpick.json")),
]

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def t(ts):
    return time.strftime("%m-%d %H:%M:%S", time.localtime(ts))


def pid_alive(pid):
    try:
        h = icall.k32.OpenProcess(0x1000, False, int(pid))  # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return False
        icall.k32.CloseHandle(h)
        return True
    except Exception:
        return False


def main():
    print("=" * 66)
    print("客户端 hook 体检（只读）")
    print("=" * 66)

    pid = icall.find_pid()
    if not pid:
        print("游戏没在运行 —— 这种状态下不可能残留任何 hook（内存随进程消失）")
        return 2
    base = icall.find_module_base(pid)
    h = icall.k32.OpenProcess(0x0410 | 0x0020 | 0x0008, False, pid)
    if not base or not h:
        print("拿不到模块基址 / 打开进程失败")
        return 2

    try:
        import psutil  # 可选，只用来打印启动时间
        started = psutil.Process(pid).create_time()
    except Exception:
        started = None
    print("进程 pid   : %d" % pid)
    print("模块基址   : %#x" % base)
    if started:
        print("启动时间   : %s" % t(started))

    print("\n[1] 内存补丁点（live 与磁盘原文件逐字节对比）")
    dirty = []
    for name, rva, note in POINTS:
        live = icall.read_mem(h, base + rva, 16) or b""
        orig = icall.file_bytes(rva, 16) or b""
        bad = live != orig
        if bad:
            dirty.append((name, rva, live, orig))
        print("  %-38s %s" % (name, "已挂钩 ✗" if bad else "原始 ✓"))
        if bad:
            print("      live %s" % live.hex(" "))
            print("      file %s" % orig.hex(" "))
    icall.k32.CloseHandle(h)

    print("\n[2] 客户端文件是否被打过补丁")
    for f, want in (("BH3.exe", 2023), ("BH3_Data/Native/UserAssembly.dll", 2023)):
        p = os.path.join(ROOT, f.replace("/", os.sep))
        if os.path.exists(p):
            mt = time.localtime(os.path.getmtime(p))
            flag = "✓ 原版" if mt.tm_year <= want else "✗ 被改过"
            print("  %-40s %s  %s" % (f, t(os.path.getmtime(p)), flag))
        else:
            print("  %-40s 不存在" % f)

    print("\n[3] 注入日志：有没有在本次启动之后又跑过 rehook")
    for name in ("rehook_log.txt", "rehook_abyss_log.txt", "rehook_qt_log.txt"):
        p = os.path.join(ROOT, name)
        if not os.path.exists(p):
            print("  %-24s 无" % name)
            continue
        mt = os.path.getmtime(p)
        if started and mt > started:
            print("  %-24s %s  ✗ 晚于本次启动（启动后又注入过）" % (name, t(mt)))
        else:
            print("  %-24s %s  ✓ 早于本次启动" % (name, t(mt)))

    print("\n[4] 服务端跑的是不是实验版")
    dll = os.path.join(ROOT, "server-v2", "run", "Server.dll")
    if os.path.exists(dll):
        blob = open(dll, "rb").read()
        marks = [b"SingleAbyss", b"OWEndlessSingleModeStage", b"PreGeneralActivityId",
                 b"GetGeneralActivityGetMainInfoReqHandler"]
        hit = [m.decode() for m in marks if m in blob]
        print("  Server.dll 生成于 %s" % t(os.path.getmtime(dll)))
        print("  实验期符号 : %s" % ("仍存在 ✗ " + ",".join(hit) if hit else "无 ✓（已回退）"))
    else:
        print("  找不到 Server.dll")

    print("\n[5] 旧状态文件（自查时最容易被它误导）")
    for label, p in STATE_FILES:
        if not os.path.exists(p):
            print("  %-10s 不存在 ✓" % label)
            continue
        try:
            d = json.load(open(p))
        except Exception:
            print("  %-10s 无法解析，建议删除" % label)
            continue
        opid = d.get("pid")
        alive = pid_alive(opid) if opid else False
        print("  %-10s 记录的 pid=%s %s" % (label, opid, "仍存活" if alive else "已退出（过期）✗"))

    print("\n" + "=" * 66)
    if dirty:
        print("结论：发现 %d 处内存补丁 —— 当前进程确实被 hook 了" % len(dirty))
        print("      撤销：python rea/_rea/icall.py uninstall")
        return 1
    print("结论：内存干净 —— 没有任何 hook 存活；重启后看到的任何「深渊」")
    print("      都不可能是 hook 残留，只可能来自客户端本地表或服务端下发。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
