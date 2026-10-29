#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mon.py — 远端 Ghidra 全量分析进度监控（本地运行，SSH 拉取快照）

用法:
    mon.py            # 打一次快照
    mon.py -w 30      # 每 30 秒刷新一次（Ctrl-C 退出）
    mon.py --proj bh3full   # 指定工程名（默认自动挑最新的 .rep）

它回答三件事:
    1. 还活着吗 / 烧多少 CPU / 吃多少内存（离 OOM 还有多远）
    2. 跑到哪个 analyzer 了（Ghidra 日志里的 ANALYZING 行）
    3. 数据库在不在长（db.2.gbf 体积 + 每分钟增量），停了就是卡死或结束
"""
import sys
import os
import re
import json
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 自举：把 _pylibs（paramiko）加进搜索路径，这样双击 mon.py 也能跑
_LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_pylibs")
if os.path.isdir(_LIB) and _LIB not in sys.path:
    sys.path.insert(0, _LIB)
import rsh

STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".mon_state.json")


def sh(cli, cmd, timeout=40):
    rc, out, err = rsh.run(cli, cmd, timeout=timeout)
    return out


def parse_kv(out, tag):
    """抓 ===TAG=== 到下一个 === 之间的内容"""
    m = re.search(r"===%s===\n(.*?)(?=\n===|\Z)" % tag, out, re.S)
    return m.group(1).strip() if m else ""


def parse_sub(out, tag):
    """抓 ---TAG--- 到下一个 ---xxx--- 之间的内容"""
    m = re.search(r"---%s---\n(.*?)(?=\n---[a-z]+---|\Z)" % tag, out, re.S)
    return m.group(1).strip() if m else ""


def human(nbytes):
    n = float(nbytes)
    for u in ("B", "K", "M", "G", "T"):
        if n < 1024:
            return "%.1f%s" % (n, u)
        n /= 1024
    return "%.1fP" % n


def snapshot(cli, proj_name=None):
    # 一次 SSH 往返拿全部信息，避免多次握手
    proj_sel = ""
    if proj_name:
        proj_sel = 'P=$(ls -d ~/re/ghidra/%s/*.rep 2>/dev/null | head -1)' % proj_name
    else:
        proj_sel = 'P=$(ls -dt ~/re/ghidra/*/*.rep 2>/dev/null | head -1)'

    cmd = r"""
echo ===NOW===; date '+%Y-%m-%d %H:%M:%S'
echo ===MARKER===
echo ===PROC===
ps -eo pid,pcpu,pmem,rss,etime,comm --sort=-rss 2>/dev/null \
  | awk 'NR>1 && $6 ~ /^java/ {print $1, $2, $3, $4, $5, $6}' | head -3
echo ===XMX===
for q in $(ps -eo pid,comm --sort=-rss 2>/dev/null | awk '$2 ~ /^java/ {print $1}' | head -1); do
  tr '\0' '\n' < /proc/$q/cmdline 2>/dev/null | grep -E '^-Xmx' || echo '(unknown)'
done
echo ===STALE===
ps -eo pid,rss,etime,comm --sort=-rss 2>/dev/null \
  | awk 'NR>1 && $4=="MainThread" {print $1, $2, $3}' | head -2
echo ===REANODE===
for q in $(ls /proc | grep -E '^[0-9]+$'); do
  tr '\0' ' ' < /proc/$q/cmdline 2>/dev/null | grep -q 'rea mcp' && echo "$q"
done | head -1
echo ===MEM===; free -m | sed -n '2,3p'
echo ===DISK===; df -h /home | tail -1
echo ===LOAD===; cat /proc/loadavg
echo ===OOM===
dmesg 2>/dev/null | grep -ci 'Out of memory' || echo 0
echo ===PILOT===
PD=$(ls -dt ~/re/pilot_*/ 2>/dev/null | head -1)
echo "dir=$PD"
if [ -n "$PD" ]; then
  cat "$PD/meta.txt" 2>/dev/null
  echo "---last---"
  tail -1 "$PD/rss.txt" 2>/dev/null
fi
echo ===PROJ===
@@P@@
echo "$P"
if [ -n "$P" ]; then
  du -sb "$P" 2>/dev/null | cut -f1
    find "$P" -name 'db*.gbf' -printf '%T@ %s\n' 2>/dev/null | sort -rn | head -1
fi
echo ===LOG===
if [ -n "$P" ]; then
  D=$(dirname "$P")
  L=$(ls -t "$D"/*.log "$D"/*.out ~/re/ghidra/*.log ~/re/ghidra/*.out \
        ~/re/*/run.out ~/re/pilot_*.log 2>/dev/null | head -1)
  echo "file=$L"
  if [ -n "$L" ]; then
    echo "---size---"; stat -c %s "$L" 2>/dev/null
    echo "---analyz---"
    grep -aiE 'ANALYZ|Analyzer|REPORT: (Save|Processing|Import)|PROGRESS |CALLGRAPH-DONE|FUNCCOUNT total' "$L" 2>/dev/null | tail -4
    echo "---tail---"
    tail -4 "$L" 2>/dev/null | cut -c1-160
    echo "---func---"
    grep -aE 'FUNCCOUNT total|CALLGRAPH-DONE' "$L" 2>/dev/null | tail -2 | cut -c1-160
  fi
fi
"""
    cmd = cmd.replace("@@P@@", proj_sel)
    out = sh(cli, cmd, timeout=60)
    snap = {"ts": time.time(), "raw": out}

    now = parse_kv(out, "NOW")
    proc = parse_kv(out, "PROC")
    xmx = parse_kv(out, "XMX").strip()
    stale = parse_kv(out, "STALE").strip()
    reanode = parse_kv(out, "REANODE").strip().split("\n")[0].strip()
    mem = parse_kv(out, "MEM")
    disk = parse_kv(out, "DISK")
    load = parse_kv(out, "LOAD")
    oom = parse_kv(out, "OOM")
    pilot = parse_kv(out, "PILOT")
    proj = parse_kv(out, "PROJ")
    log = parse_kv(out, "LOG")

    lines = []
    lines.append("┌─ 快照 %s" % now)

    # --- 进程 ---
    if proc.strip() and len(proc.strip().split("\n")[0].split()) >= 5:
        p = proc.strip().split("\n")[0].split()
        pid, cpu, pmem, rss, etime = p[0], p[1], p[2], p[3], p[4]
        rss_mb = int(rss) / 1024.0
        lines.append("│ 进程  PID %-7s CPU %5s%%  RSS %7.0f MB  已运行 %s" %
                     (pid, cpu, rss_mb, etime))
        if xmx and xmx != "(unknown)":
            lines.append("│ 堆    上限 %s" % xmx)
        snap["rss_mb"] = rss_mb
        snap["cpu"] = cpu
        snap["pid"] = pid
    else:
        lines.append("│ 进程  ✗ 无 java 进程（已结束 / 未启动）")
        snap["rss_mb"] = 0
        if stale:
            s = stale.split("\n")[0].split()
            if reanode and s[0] == reanode:
                lines.append("│ 注    PID %s 是 rea MCP 服务（node），非僵尸，勿杀" % s[0])
            else:
                lines.append("│ ⚠ 残留 java 进程 PID %s 占 %.0f MB（可 kill 回收）" %
                             (s[0], int(s[1]) / 1024.0))

    # --- 内存 ---
    mt = re.search(r"^Mem:\s+(\d+)\s+(\d+)\s+(\d+)\s+\d+\s+\d+\s+(\d+)\s*$", mem, re.M)
    sw = re.search(r"^Swap:\s+(\d+)\s+(\d+)\s+(\d+)", mem, re.M)
    if mt:
        tot, used, free_, avail = (int(x) for x in mt.groups())
        lines.append("│ 内存  %5.0f / %5.0f MB 已用   可用 %5.0f MB" % (used, tot, avail))
        snap["mem_avail"] = avail
        if sw:
            su = int(sw.group(2))
            lines.append("│ Swap  已用 %5.0f MB" % su)
            snap["swap_used"] = su
            if su > 200:
                lines.append("│ ⚠ 已经在用 swap —— 物理内存不够，速度会掉一个量级")

    # --- 磁盘 / load / OOM ---
    if disk:
        lines.append("│ 磁盘  %s" % " ".join(disk.split()[-4:]))
    if load:
        lines.append("│ 负载  %s" % load)
    try:
        if int(oom.strip().split("\n")[0]) > 0:
            lines.append("│ ⚠ 内核日志里出现过 Out of memory —— 之前被 OOM kill 过")
    except Exception:
        pass

    # --- 工程体积增长 ---
    pl = [x for x in proj.split("\n") if x.strip()]
    snap["proj_size"] = 0
    if len(pl) >= 2 and pl[1].strip().isdigit():
        size = int(pl[1].strip())
        snap["proj_size"] = size
        rate = ""
        try:
            st = json.load(open(STATE))
            dt = snap["ts"] - st["ts"]
            if dt > 5 and st.get("proj_size"):
                d = size - st["proj_size"]
                rate = "  (%+.1f MB, %+.1f MB/min)" % (
                    d / 1048576.0, d / 1048576.0 / (dt / 60.0))
        except Exception:
            pass
        lines.append("│ 工程  %s  %s%s" % (pl[0].strip(), human(size), rate))
        # 最新 db 文件的写入时间（Ghidra 只在保存时落盘，分析中长时间不写属正常）
        if len(pl) >= 3:
            parts = pl[2].split()
            if len(parts) >= 2:
                age = time.time() - int(float(parts[0]))
                note = "保存时才会写，分析中不写属正常" if age > 120 else "正在落盘"
                lines.append("│ 落盘  最新 db %s   %s 前（%s）" %
                             (human(int(parts[1])), "%ds" % age, note))

    # --- 日志 / analyzer ---
    log_size = 0
    log_age = None
    if log:
        try:
            log_size = int(parse_sub(log, "size").strip().split("\n")[0])
        except Exception:
            log_size = 0
        an = parse_sub(log, "analyz").split("\n")
        an = [a.strip() for a in an if a.strip()]
        if an:
            last = an[-1][-110:]
            lines.append("│ 阶段  %s" % last)
            snap["analyzer"] = last
        tl = parse_sub(log, "tail").split("\n")
        tl = [t.strip() for t in tl if t.strip()]
        if tl:
            lines.append("│ 日志  %s" % tl[-1][:110])
            if "Save succeeded" in tl[-1]:
                lines.append("│ ✅ 检测到 Save succeeded —— 这一轮跑完了")
        fn = parse_sub(log, "func").strip()
        if fn:
            for ln in fn.split("\n"):
                if "FUNCCOUNT total" in ln or "CALLGRAPH-DONE" in ln:
                    lines.append("│ 结果  %s" % ln.split(">")[-1].strip()[:120])
                    break
            else:
                lines.append("│ 结果  %s" % fn.split("\n")[-1].strip()[:110])

    # --- 最近一次运行汇总（进程不在时也有信息） ---
    if pilot:
        pdir = ""
        mm = re.search(r"^dir=(.*)$", pilot, re.M)
        if mm:
            pdir = mm.group(1).strip()
        kv = dict(re.findall(r"(\w+)=([\w.]+)", pilot))
        if kv.get("peakRssMb"):
            dur = ""
            try:
                dur = "  耗时 %d 秒" % (int(kv["end"]) - int(kv["start"]))
            except Exception:
                pass
            lines.append("│ 汇总  %s%s" % (pdir.rstrip("/").rsplit("/", 1)[-1], dur))
            lines.append("│       峰值 RSS %s MB   最低可用 %s MB   %d 个采样点" % (
                kv.get("peakRssMb", "?"), kv.get("minAvailMb", "?"),
                int(kv.get("samples", 0) or 0)))
            if kv.get("rc") is not None:
                lines.append("│       rc=%s%s" % (
                    kv["rc"], "（正常退出）" if kv["rc"] == "0" else "（异常）"))

    # --- 活性判断：日志增长 + CPU ---
    verdict = None
    alive = bool(snap.get("rss_mb"))
    try:
        st = json.load(open(STATE))
        dt = snap["ts"] - st["ts"]
        if dt > 5 and st.get("log_size"):
            d = log_size - st["log_size"]
            lines.append("│ 日志增 %+.1f KB / %.0f 秒" % (d / 1024.0, dt))
            # 只有进程还活着才谈"卡死"
            if alive and d <= 0 and dt > 600 and float(snap.get("cpu", 0) or 0) < 5:
                verdict = "疑似卡死（日志 10 分钟无增长且 CPU<5%）"
    except Exception:
        pass

    if not alive:
        verdict = "已结束（进程不在）；工程已落盘，可复用"

    # --- 综合风险 ---
    if snap.get("rss_mb"):
        av = snap.get("mem_avail", 9999)
        if av < 400:
            verdict = "内存告急，可用仅 %d MB，随时可能 OOM" % av
        elif snap.get("swap_used", 0) > 200:
            verdict = "已在使用 swap，速度会掉一个量级"
    lines.append("│ 判定  %s" % (verdict if verdict else "正常"))

    lines.append("└" + "─" * 60)
    print("\n".join(lines))

    # 存状态给下次算速率
    try:
        json.dump({"ts": snap["ts"], "proj_size": snap["proj_size"],
                   "log_size": log_size}, open(STATE, "w"))
    except Exception:
        pass
    return snap


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-w", "--watch", type=int, default=0, help="每 N 秒刷新")
    ap.add_argument("--proj", default=None, help="工程名，如 bh3full")
    a = ap.parse_args()

    cli = rsh.conn()
    try:
        if a.watch <= 0:
            snapshot(cli, a.proj)
        else:
            while True:
                os.system("cls" if os.name == "nt" else "clear")
                snapshot(cli, a.proj)
                time.sleep(a.watch)
    except KeyboardInterrupt:
        print("\n(停止监控)")
    finally:
        cli.close()


if __name__ == "__main__":
    main()
