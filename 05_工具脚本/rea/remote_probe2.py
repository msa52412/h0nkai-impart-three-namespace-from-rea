#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""远端探测 2：rea 服务、Ghidra 位置、已有工程。"""
import paramiko

HOST = "192.168.0.104"
USER = "nas"
PWD = "mt#win7"

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, 22, USER, PWD, timeout=15, allow_agent=False, look_for_keys=False)

CMDS = [
    ("opt", "ls -la ~/opt; echo ---; ls ~/opt/* | head -40"),
    ("re", "ls -la ~/re; echo ---; find ~/re -maxdepth 2 | head -40"),
    ("artifacts", "ls -la ~/rea_artifacts | head -20"),
    ("test", "ls -la ~/test | head"),
    ("ghidra-deep", "find ~ /opt /usr/local /home -maxdepth 5 -iname '*ghidra*' 2>/dev/null | head -20"),
    ("proc", "ps -ef | grep -i -E 'rea|ghidra|node|java' | grep -v grep | head -20"),
    ("listen", "ss -lntp 2>/dev/null | head -20"),
    ("history", "cat ~/.bash_history 2>/dev/null | tail -40"),
]
for name, cmd in CMDS:
    _, so, se = cli.exec_command(cmd, timeout=120)
    out = so.read().decode("utf-8", "replace").strip()
    err = se.read().decode("utf-8", "replace").strip()
    print("\n=== %s ===" % name)
    print(out[:3000] if out else "(空)")
    if err:
        print("[stderr]", err[:200])
cli.close()
