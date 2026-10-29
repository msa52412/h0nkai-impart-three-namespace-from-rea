#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prog_bodies.py — 本地查看「反编译体导出」进度

用法:
    python prog_bodies.py              # 打一次快照
    python prog_bodies.py -w 30        # 每 30 秒刷新（Ctrl-C 退出）

看四件事:
    1. 导出到第几个 / 总共多少（PROGRESS 行 + bodies.tsv 实际行数）
    2. 瞬时速率（两次采样算，比日志里的累计均值准——均值被启动加载摊薄了）
    3. 剩余时间，以及**已覆盖多少个 C# 方法**（把地址反查回方法表）
    4. 远端磁盘 / 内存还剩多少

方法覆盖率要读 398k 行的方法地址表，首次约 2 秒，之后走缓存。
"""
import argparse
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
HOST = "nas@192.168.0.104"
KEY = os.path.expanduser("~/.ssh/rea_remote")
REMOTE_BODIES = "~/re/sym/bodies.tsv"
REMOTE_LOG = "~/re/sym/bodies_full.log"
REMOTE_LIST = "~/re/sym/body_list.txt"
TOTAL = 311382

_total_methods = None      # 408458
_addr_methods = None       # va(RVA) -> 该方法地址服务多少个 C# 方法


def ssh(cmd, timeout=40):
    p = subprocess.run(
        ["ssh", "-i", KEY, "-o", "StrictHostKeyChecking=no",
         "-o", "ConnectTimeout=10", HOST, cmd],
        capture_output=True, text=True, timeout=timeout)
    return p.stdout


def snapshot():
    """一次 SSH 往返拿全部远端指标"""
    cmd = (
        'printf "%%s\\n" "$(wc -l < %s)";'
        'grep PROGRESS %s | tail -2;'
        'printf "%%s\\n" "===MARK===";'
        'printf "%%s\\n" "$(df --output=avail -BG /home | tail -1 | tr -d " G")";'
        'printf "%%s\\n" "$(free -m | awk \'/Mem:/{print $7}\')";'
        'printf "%%s\\n" "$(pgrep -f "analyzeHead[less]" | wc -l)"'
        % (REMOTE_BODIES, REMOTE_LOG)
    )
    out = ssh(cmd).split("\n")
    r = {"lines": 0, "progs": [], "disk": "?", "mem": "?", "alive": "0"}
    mark = -1
    for i, ln in enumerate(out):
        if ln.strip() == "===MARK===":
            mark = i
            break
    head = out[:mark] if mark > 0 else out
    tail_ = [x.strip() for x in out[mark + 1:] if x.strip()] if mark > 0 else []
    for ln in head:
        ln = ln.strip()
        if not ln:
            continue
        if "PROGRESS" in ln:
            r["progs"].append(ln)
        else:
            try:
                r["lines"] = int(ln)
            except ValueError:
                pass
    for i, key in enumerate(["disk", "mem", "alive"]):
        if i < len(tail_):
            r[key] = tail_[i]
    return r


_PROG_RE = re.compile(
    r"PROGRESS (\d+)/(\d+)\s+([\d.]+) 个/秒.*?miss=(\d+) empty=(\d+)")


def steady_rate(progs):
    """从最后两条 PROGRESS 反推稳态速率。

    日志里 rate = ok*1000/ms（ok 是从启动累计的成功数，ms 是从启动算的毫秒），
    所以 ms_i = ok_i/rate_i*1000；两次相减即可消掉「加载工程」那段固定开销。
    """
    pts = []
    for ln in progs:
        m = _PROG_RE.search(ln)
        if m:
            n, tot, rate, miss, empty = m.groups()
            n, rate, miss, empty = int(n), float(rate), int(miss), int(empty)
            ok = n - miss - empty
            if rate > 0 and ok > 0:
                pts.append((n, ok, ok / rate * 1000.0))   # (n, ok, ms)
    if len(pts) < 2:
        return None, None
    (n1, ok1, ms1), (n2, ok2, ms2) = pts[-2], pts[-1]
    dms = ms2 - ms1
    dn = n2 - n1
    if dms <= 0 or dn <= 0:
        return None, None
    return dn / dms * 1000.0, (n2, dn, dms / 1000.0)


def load_addr_methods():
    """方法地址表 → {rva: 该地址被多少个方法用}。返回 (总方法数, 字典)"""
    global _total_methods, _addr_methods
    if _addr_methods is not None:
        return _total_methods, _addr_methods
    p = os.path.join(HERE, "bh3_method_addr.tsv")
    d = {}
    n = 0
    if os.path.exists(p):
        with open(p, encoding="utf-8", errors="replace") as f:
            f.readline()
            for ln in f:
                q = ln.rstrip("\r\n").split("\t")
                if len(q) < 5:
                    continue
                n += 1
                if not q[3]:
                    continue          # 外部程序集的方法没有原生地址
                try:
                    rva = int(q[3], 16)   # 这一列是十六进制字符串
                except ValueError:
                    continue
                d[rva] = d.get(rva, 0) + 1
    _total_methods, _addr_methods = n, d
    return _total_methods, _addr_methods


def local_bodies():
    """本地 bodies.tsv 里的 VA 集合（转成 RVA）"""
    p = os.path.join(HERE, "bodies.tsv")
    s = set()
    if not os.path.exists(p):
        return s, 0
    with open(p, encoding="utf-8", errors="replace") as f:
        for ln in f:
            t = ln.find("\t")
            if t > 0:
                try:
                    s.add(int(ln[:t], 16) - 0x180000000)
                except ValueError:
                    pass
    return s, os.path.getsize(p)


def bar(frac, width=34):
    k = int(frac * width)
    return "█" * k + "·" * (width - k)


def show(prev=None):
    s = snapshot()
    now = time.time()

    print("\033[2J\033[H", end="")          # 清屏
    print("═══ 反编译体导出进度 ═══  %s" % time.strftime("%H:%M:%S"))
    print()

    if str(s["alive"]) == "0":
        print("  ⚠ 远端没有 analyzeHeadless 进程 —— 已结束或被终止")
    else:
        print("  远端进程在跑")

    lines = s["lines"]
    frac = lines / float(TOTAL)
    print("  地址进度  %s  %5.1f%%   %s / %s"
          % (bar(frac), frac * 100, f"{lines:,}", f"{TOTAL:,}"))

    # 速率：优先用日志两次 PROGRESS 反推的稳态值（文件有 4 MB 写缓冲，
    # 每 500 条约 60 秒才落盘，短窗口采样会一直读到 0）
    rate, info = steady_rate(s["progs"])
    if prev:
        dt = now - prev[0]
        dn = lines - prev[1]
        if dt > 60 and dn > 0:
            rate = dn / dt
            info = (lines, dn, dt)
    if rate:
        print("  稳态速率  %.2f 个/秒            （%d 秒内推进 %d 个）"
              % (rate, info[2], info[1]))

    if s["progs"]:
        print()
        print("  远端日志：%s" % s["progs"][-1].replace(
            "INFO  DumpBodies.java> ", "").replace(" (GhidraScript)", ""))

    # 方法覆盖
    tot_m, amap = load_addr_methods()
    bset, bsize = local_bodies()
    hit = sum(amap.get(r, 0) for r in bset) if (tot_m and bset) else 0
    if tot_m:
        f2 = hit / float(tot_m)
        print()
        print("  方法覆盖  %s  %5.1f%%   %s / %s"
              % (bar(f2), f2 * 100, f"{hit:,}", f"{tot_m:,}"))
        print("            （本地 bodies.tsv %d 条 / %.1f MB）"
              % (len(bset), bsize / 1048576.0))

    # ETA
    left = TOTAL - lines
    if rate and rate > 0.05:
        print()
        print("  剩余 %s 个  →  约 %.1f 小时"
              % (f"{left:,}", left / rate / 3600))
    print()
    print("  远端磁盘剩余 %s G   ·   可用内存 %s MB" % (s["disk"], s["mem"]))
    print()
    print("  刷新源码树： scp nas@192.168.0.104:~/re/sym/bodies.tsv . "
          "&& python gen_cs.py --out src --bodies bodies.tsv")
    return (now, lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-w", "--watch", type=int, default=0,
                    help="每 N 秒刷新一次，0 = 只打一次")
    a = ap.parse_args()

    prev = None
    if a.watch <= 0:
        show()
        return
    try:
        while True:
            prev = show(prev)
            time.sleep(max(5, a.watch))
    except KeyboardInterrupt:
        print("\n退出")


if __name__ == "__main__":
    main()
