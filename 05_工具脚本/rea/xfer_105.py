#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 104 的 Ghidra 工程 + 脚本直接推到 105（内网直传，不经本地）。"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_pylibs"))
import rsh2

SRC = "~/re/ghidra"

cmd = r"""
set -e
echo '--- 1. 目标目录 ---'
ssh -o BatchMode=yes -o StrictHostKeyChecking=no nas@192.168.0.105 'mkdir -p ~/re/ghidra ~/re/sym && echo ok' 2>/dev/null

echo '--- 2. 传 proj4 + scripts (tar 单流) ---'
cd ~/re/ghidra
T0=$(date +%s)
tar -cf - --exclude='bh3fix.lock' --exclude='bh3fix.lock~' proj4 scripts \
  | ssh -o BatchMode=yes nas@192.168.0.105 'tar -C ~/re/ghidra -xf - && echo XFER_OK'
T1=$(date +%s)
echo "耗时 $((T1-T0)) 秒"

echo '--- 3. 校验 ---'
ssh -o BatchMode=yes nas@192.168.0.105 'echo -n "105 proj4: "; du -sh ~/re/ghidra/proj4 | cut -f1; echo -n "105 文件数: "; find ~/re/ghidra/proj4 -type f | wc -l; echo -n "105 scripts: "; ls ~/re/ghidra/scripts | wc -l; echo -n "105 磁盘剩余: "; df -h /home | tail -1 | cut -d" " -f1'
echo -n '104 proj4: '; du -sh ~/re/ghidra/proj4 | cut -f1
"""

cli = rsh2.conn("104", timeout=30)
cli.get_transport().set_keepalive(30)
print("开始传输 ...")
t0 = time.time()
rc, o, e = rsh2.run(cli, cmd, timeout=3000)
cli.close()
print(o)
if e.strip():
    print("STDERR:", e[-3000:])
print("rc=%d  总耗时 %.1f 秒" % (rc, time.time() - t0))
