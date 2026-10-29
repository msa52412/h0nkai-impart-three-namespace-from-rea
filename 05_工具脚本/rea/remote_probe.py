#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""远端探测（只读）：连通性 / 系统信息 / 是否装 Ghidra / 磁盘余量。"""
import sys

import paramiko

HOST = "192.168.0.104"
USER = "nas"
PWD = "mt#win7"

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15,
            allow_agent=False, look_for_keys=False)
print("连接成功:", HOST)

CMDS = [
    ("uname", "uname -a"),
    ("df -h", "df -h / /volume1 /home 2>/dev/null | head -20"),
    ("home", "pwd; ls -la ~ | head -30"),
    ("ghidra", "ls -d ~/ghidra* /opt/ghidra* /usr/local/ghidra* /volume*/ghidra* 2>/dev/null"),
    ("java", "java -version 2>&1 | head -3"),
    ("python", "python3 -V 2>&1"),
    ("find-ghidra", "find / -maxdepth 4 -iname 'analyzeHeadless' 2>/dev/null | head -5"),
]
for name, cmd in CMDS:
    stdin, stdout, stderr = cli.exec_command(cmd, timeout=60)
    out = stdout.read().decode("utf-8", "replace").strip()
    err = stderr.read().decode("utf-8", "replace").strip()
    print("\n=== %s ===" % name)
    print(out[:2000] if out else "(空)")
    if err:
        print("[stderr]", err[:300])
cli.close()
