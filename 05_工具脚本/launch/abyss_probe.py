#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""深渊协议探针 —— 看客户端到底发了哪些深渊相关请求，以及服务端实现了没有。

为什么需要它
------------
7.0 客户端的 UI 逻辑在加密的 asset bundle 里（lua），静态解不开；
但服务端日志会记下**每一个**收到的 CmdId（Session.ProcessPacket → c.Log(name)），
没实现的还会打 `Xxx not handled!`。所以「客户端有没有某个入口」这件事，
让客户端自己跑一遍、再看日志，比逆向快得多也准得多。

用法
----
    tools\\python\\python.exe _launch\\abyss_probe.py
    tools\\python\\python.exe _launch\\abyss_probe.py --log _launch/logs/v2_Server.log
    tools\\python\\python.exe _launch\\abyss_probe.py --all      # 不只深渊，全部协议都列

输出三块：
    [1] 客户端发过的深渊协议（次数 + 服务端有没有 handler）
    [2] 声明了但客户端一次没发过的（= 客户端 UI 里没有这个入口，或者没点）
    [3] 结论提示
"""

import argparse
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTO = os.path.join(BASE, "server-v2", "Common", "Common.Resources.Proto")
HANDLERS = os.path.join(BASE, "server-v2", "Server", "Handlers")
DEFAULT_LOG = os.path.join(BASE, "_launch", "logs", "v2_Server.log")

# 深渊四套体系在协议里的标识。
# 注意：必须用「包含」而不是「开头」匹配 —— 迪拉克之海的主入口叫
# `GetOpenworldEndlessDataReq`，前缀是 Get 不是 OpenworldEndless。
# 顺序有讲究：先长后短，否则 `Endless` 会把所有东西都吞掉。
FAMILIES = [
    ("超弦空间", "UltraEndless"),       # 7.0 当前在用的
    ("迪拉克之海", "OpenworldEndless"),  # 旧版高级深渊（type=OPENWORLD）
    ("贪婪深渊", "GreedyEndless"),       # 活动形式的深渊
    ("前哨无尽", "FrontEndless"),
    ("量子奇点", "Quantum"),             # 旧版低级深渊（type=QUANTUM）
    ("通用深渊", "Endless"),             # SelectType / Status / Settle 等中立件
]


def read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def load_cmdids():
    """从全局 CmdId.cs 建 CmdId 名 -> 数字的映射。

    注意：CmdTypeEndless.cs 里的名字带 `Cmd` 前缀（CmdUltraEndlessGetMainDataReq），
    而日志打印的是全局 CmdId 枚举名（UltraEndlessGetMainDataReq）——
    两者是不同的枚举，别搞混。
    """
    table = {}
    p = os.path.join(PROTO, "CmdId.cs")
    if not os.path.isfile(p):
        return table
    for name, value in re.findall(r"^\s*(\w+) = (\d+),\s*$", read(p), re.M):
        table[name] = int(value)
    return table


def load_implemented():
    """扫 Handlers 目录，拿到 `[PacketCmdId(CmdId.Xxx)]` 里的 Xxx。"""
    done = set()
    if not os.path.isdir(HANDLERS):
        return done
    for fn in os.listdir(HANDLERS):
        if not fn.endswith(".cs"):
            continue
        for m in re.findall(r"PacketCmdId\(CmdId\.(\w+)\)", read(os.path.join(HANDLERS, fn))):
            done.add(m)
    return done


def load_sent(log_path):
    """日志里收到的包。

    两种行都要抓，第二种最容易漏：
        14:08:10 <ip:port> GetExBossInfoReq              ← 有 handler
        14:08:10 <ip:port> GetOpenworldEndlessDataReq not handled!   ← 没 handler
    只匹配第一种的话，未实现的协议会被误判成「客户端根本没发过」，
    结论就完全反了。
    """
    sent = {}
    pending = set()   # 发过、但服务端没有 handler 的
    if not os.path.isfile(log_path):
        return sent, pending
    pat = re.compile(r"^\d{2}:\d{2}:\d{2} <[\d.]+:\d+> (\w+?)( not handled!)?$")
    for line in read(log_path).splitlines():
        m = pat.match(line.strip())
        if not m:
            continue
        name = m.group(1)
        sent[name] = sent.get(name, 0) + 1
        if m.group(2):
            pending.add(name)
    return sent, pending


def family_of(cmd_name):
    for label, key in FAMILIES:
        if key in cmd_name:
            return label
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=DEFAULT_LOG)
    ap.add_argument("--all", action="store_true", help="不只深渊，列出全部收到的协议")
    args = ap.parse_args()

    cmds = load_cmdids()
    impl = load_implemented()
    sent, pending = load_sent(args.log)

    if not cmds:
        print("[ERROR] 找不到 %s 下的 CmdId.cs" % PROTO)
        return 1
    if not sent:
        print("[WARN] 日志里没有收到任何包：%s" % args.log)
        print("       先双击「启动服务端v2.bat」，进游戏把「挑战」面板点一遍，再跑本脚本。")
        return 2

    # ---------- [1] 客户端发过的深渊协议 ----------
    print("=" * 84)
    print("[1] 客户端实际发过的深渊协议")
    print("=" * 84)
    hit = 0
    for name, cid in sorted(cmds.items(), key=lambda kv: kv[1]):
        n = sent.get(name)
        if not n:
            continue
        fam = family_of(name)
        if fam is None and not args.all:
            continue
        hit += 1
        flag = "[实现]" if name in impl else "[★未实现]"
        print("  %-6d %-42s %-10s x%-4d %s" % (cid, name, fam or "-", n, flag))
    if hit == 0:
        print("  （一个都没有）—— 客户端根本没打开过深渊界面，或者 7.0 的入口不在这些协议上")

    # ---------- [2] 发过但服务端没实现 ----------
    print()
    print("=" * 84)
    print("[2] 客户端发过、但服务端没实现（= 功能缺口的精确清单）")
    print("=" * 84)
    real_pending = {n: c for n, c in sent.items() if n in pending}
    if real_pending:
        for name, c in sorted(real_pending.items(), key=lambda kv: -kv[1]):
            fam = family_of(name)
            cid = cmds.get(name, "?")
            mark = "  ★" if fam else "   "
            print("%s %-6s %-44s %-10s x%d" % (mark, cid, name, fam or "-", c))
    else:
        print("  （没有）—— 客户端发的每个包服务端都有 handler")

    # ---------- [3] 协议里有、客户端没发过 ----------
    print()
    print("=" * 84)
    print("[3] 协议里有、客户端一次没发过的（= UI 走不到，服务端补了也没人调）")
    print("=" * 84)
    for label, prefix in FAMILIES:
        miss = [n for n in cmds
                if family_of(n) == label and n.endswith("Req") and n not in sent]
        if not miss:
            continue
        print("  %s（%s）：%d 个请求没出现" % (label, prefix, len(miss)))
        for n in sorted(miss, key=lambda x: cmds[x])[:10]:
            print("      %-6d %s" % (cmds[n], n))
        if len(miss) > 10:
            print("      ... 还有 %d 个" % (len(miss) - 10))

    # ---------- [4] 全部协议（可选） ----------
    if args.all:
        print()
        print("=" * 84)
        print("[4] 客户端发过的全部协议（按次数）")
        print("=" * 84)
        for name, n in sorted(sent.items(), key=lambda kv: -kv[1]):
            print("  x%-5d %s" % (n, name))

    # ---------- 结论 ----------
    print()
    print("=" * 84)
    def req_count(label):
        return sum(c for n, c in sent.items()
                   if family_of(n) == label and n.endswith("Req"))
    ultra = req_count("超弦空间")
    ow = req_count("迪拉克之海")
    qt = req_count("量子奇点")
    greedy = req_count("贪婪深渊")
    front = req_count("前哨无尽")
    print("[结论] 请求次数  超弦=%d  迪拉克=%d  量子=%d  贪婪=%d  前哨=%d"
          % (ultra, ow, qt, greedy, front))
    ow_missing = sorted(n for n in pending if family_of(n) == "迪拉克之海")
    qt_missing = sorted(n for n in pending if family_of(n) == "量子奇点")
    if ow or qt:
        print("       ★ 客户端确实在发旧深渊的请求，说明 UI 入口还活着。")
        if ow_missing:
            print("         迪拉克之海未实现：%s" % ", ".join(ow_missing))
        if qt_missing:
            print("         量子奇点未实现：%s" % ", ".join(qt_missing))
        print("         → 补上这些 handler 就能把旧深渊点亮。")
    elif ultra:
        print("       客户端只走超弦空间这一套，旧深渊 UI 里没有入口。")
    else:
        print("       还没点开过深渊界面，先照上面 [WARN] 的提示操作一次。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
