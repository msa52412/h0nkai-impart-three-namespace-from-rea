# -*- coding: utf-8 -*-
"""连 192.168.0.105 做环境勘察，并顺手装公钥免密。"""
import os, sys, io

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "_pylibs"))

import paramiko

HOST = "192.168.0.105"
USER = "nas"
PWD  = "mt#win7"

CMDS = [
    ("CPU核心",    "nproc"),
    ("CPU型号",    "grep -m1 'model name' /proc/cpuinfo | cut -d: -f2"),
    ("内存",       "free -g | awk '/Mem:/{print \"total=\"$2\"G used=\"$3\"G avail=\"$7\"G\"}'"),
    ("磁盘/home",  "df -h /home | tail -1"),
    ("内核",       "uname -r"),
    ("系统",       "cat /etc/os-release 2>/dev/null | grep PRETTY | cut -d= -f2"),
    ("家目录",     "ls -la ~ | head -30"),
    ("是否已有Ghidra", "ls -d ~/opt/ghidra* /opt/ghidra* 2>/dev/null; which analyzeHeadless 2>/dev/null; echo '---'"),
    ("是否已有工程", "ls -d ~/re ~/re/ghidra 2>/dev/null; du -sh ~/re 2>/dev/null"),
    ("java",       "java -version 2>&1 | head -3"),
    ("已有ssh key", "ls -la ~/.ssh 2>/dev/null"),
    ("负载",       "uptime"),
    ("Python",     "python3 -V 2>&1"),
]

def run(cli, cmd, timeout=60):
    _in, out, err = cli.exec_command(cmd, timeout=timeout)
    o = out.read().decode("utf-8", "replace")
    e = err.read().decode("utf-8", "replace")
    rc = out.channel.recv_exit_status()
    return rc, o, e

def main():
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("连接 %s ..." % HOST)
    cli.connect(HOST, port=22, username=USER, password=PWD, timeout=20,
                allow_agent=False, look_for_keys=False)
    print("连接成功\n" + "=" * 60)

    for name, cmd in CMDS:
        rc, o, e = run(cli, cmd)
        txt = (o or "").strip()
        if not txt and e.strip():
            txt = e.strip()
        print("[%s] rc=%d" % (name, rc))
        for ln in txt.splitlines()[:40]:
            print("    " + ln)
        print()

    # 装公钥
    pub = os.path.expanduser("~/.ssh/rea_remote.pub")
    if os.path.exists(pub):
        key = open(pub, encoding="utf-8").read().strip()
        cmd = ("mkdir -p ~/.ssh && chmod 700 ~/.ssh && touch ~/.ssh/authorized_keys && "
               "chmod 600 ~/.ssh/authorized_keys && "
               "grep -qF '%s' ~/.ssh/authorized_keys || echo '%s' >> ~/.ssh/authorized_keys; "
               "wc -l < ~/.ssh/authorized_keys" % (key, key))
        rc, o, e = run(cli, cmd)
        print("[装公钥] rc=%d authorized_keys 行数=%s" % (rc, o.strip()))
    else:
        print("[装公钥] 本地没有 %s，跳过" % pub)

    cli.close()
    print("\n完成")

if __name__ == "__main__":
    main()
