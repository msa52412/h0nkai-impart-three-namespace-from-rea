#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rx.py — 在远端执行一段 shell（从文件读，避免引号/变量展开地狱）

用法:
    rx.py <cmd.sh>        # 执行本地脚本文件里的命令
    rx.py -e 'cmd'        # 直接给一条命令
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rsh

if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(1)

if sys.argv[1] == "-e":
    cmd = sys.argv[2]
else:
    cmd = open(sys.argv[1], encoding="utf-8").read()

cli = rsh.conn()
rc, out, err = rsh.run(cli, cmd, timeout=120)
print(out)
if err.strip():
    print("--- STDERR ---")
    print(err[:2000])
print("--- RC=%d ---" % rc)
cli.close()
