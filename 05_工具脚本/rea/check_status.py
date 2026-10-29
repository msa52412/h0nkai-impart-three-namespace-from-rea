#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键检查 rea 主机上的 Ghidra 分析是否完成。

用法:
    python check_status.py

判定逻辑（三个判据，必须同时满足才算"做完"）:
    1. 进程     远端没有 AnalyzeHeadless 进程了
    2. 产物     目标 .c 文件存在且大小 > 0
    3. 收尾     日志里出现 "Post-analysis succeeded"
"""
import subprocess
import sys

HOST = "nas@192.168.0.104"
KEY = r"C:\Users\Administrator\.ssh\rea_remote"

SSH = [
    "ssh", "-i", KEY,
    "-o", "BatchMode=yes",
    "-o", "StrictHostKeyChecking=accept-new",
    "-o", "LogLevel=ERROR",
    HOST,
]

REMOTE = r"""
echo "TIME=$(date '+%H:%M:%S')"
echo "PROCS=$(pgrep -c java 2>/dev/null || echo 0)"
echo "DEC_CORE=$(stat -c %s /home/nas/re/dec_core.c 2>/dev/null || echo 0)"
echo "DEC_TARGETS=$(stat -c %s /home/nas/re/dec_targets.c 2>/dev/null || echo 0)"
echo "OK_MARK=$(grep -c 'Post-analysis succeeded' /home/nas/re/ghidra/run2.out 2>/dev/null || echo 0)"
echo "DONE_FUNCS=$(grep -c 'DumpDecomp: done' /home/nas/re/ghidra/run2.out 2>/dev/null || echo 0)"
echo "FAIL=$(grep -ciE 'analysis failed|out of memory|OutOfMemoryError|Exception in thread' /home/nas/re/ghidra/run2.out 2>/dev/null || echo 0)"
echo "TAIL_BEGIN"
tail -c 400 /home/nas/re/ghidra/run2.out 2>/dev/null
echo
echo "TAIL_END"
"""


def main():
    try:
        out = subprocess.run(SSH + [REMOTE], capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        print("SSH 超时 —— 检查网络或主机是否开机")
        return 1
    if out.returncode != 0 and not out.stdout:
        print("SSH 失败:", out.stderr.strip())
        return 1

    kv = {}
    tail, in_tail = [], False
    for line in out.stdout.splitlines():
        if line.strip() == "TAIL_BEGIN":
            in_tail = True
            continue
        if line.strip() == "TAIL_END":
            in_tail = False
            continue
        if in_tail:
            tail.append(line)
        elif "=" in line:
            k, _, v = line.partition("=")
            kv[k.strip()] = v.strip()

    procs = int(kv.get("PROCS", "0") or 0)
    core = int(kv.get("DEC_CORE", "0") or 0)
    tgts = int(kv.get("DEC_TARGETS", "0") or 0)
    okmark = int(kv.get("OK_MARK", "0") or 0)
    donef = int(kv.get("DONE_FUNCS", "0") or 0)
    fails = int(kv.get("FAIL", "0") or 0)

    print("远端时间        : %s" % kv.get("TIME", "?"))
    print("java 进程数     : %d  %s" % (procs, "运行中" if procs else "已退出"))
    print("dec_core.c      : %d 字节 %s" % (core, "✅" if core > 0 else "❌"))
    print("dec_targets.c   : %d 字节 %s" % (tgts, "✅" if tgts > 0 else "❌"))
    print("已导出函数数    : %d" % donef)
    print("收尾标记        : %d  %s" % (okmark, "✅" if okmark else "❌"))
    print("失败/异常关键字 : %d  %s" % (fails, "⚠ 需检查" if fails else "✅ 无"))
    print()

    if procs > 0:
        print(">>> 状态：仍在分析中，等一会儿再跑一次")
    elif core > 0 and okmark > 0:
        print(">>> 状态：✅ 做完了，可以拉产物了")
        print("    scp -i %s %s:/home/nas/re/dec_core.c D:\\Carol-start\\_rea\\" % (KEY, HOST))
    elif procs == 0 and core == 0:
        print(">>> 状态：❌ 进程没了但没产物 —— 失败了，看下面日志")
    else:
        print(">>> 状态：⚠ 异常，看下面日志")

    if tail:
        print("\n--- 日志尾部 ---")
        print("\n".join(tail[-15:]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
