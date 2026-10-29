#!/usr/bin/env python
"""SSH 探测远端 NAS：内存/CPU/磁盘 + rea/Ghidra/node 安装情况 + /tmp/bh3 文件。"""
import sys
import paramiko

HOST = sys.argv[1] if len(sys.argv) > 1 else "192.168.0.105"
USER, PW = "nas", "mt#win7"

CMDS = [
    ("内存", "free -g | head -2; echo '--- 可用(MB) ---'; free -m | awk '/Mem:/{print $7\" MB available / \"$2\" MB total\"}'"),
    ("CPU", "nproc; grep -m1 'model name' /proc/cpuinfo"),
    ("交换分区", "free -g | awk '/Swap/{print $2\" GB\"}'"),
    ("磁盘", "df -h /tmp /home 2>/dev/null | tail -3"),
    ("rea", "ls -la ~/.local/bin/rea 2>/dev/null && readlink -f ~/.local/bin/rea"),
    ("Ghidra", "ls -d ~/opt/ghidra* 2>/dev/null; grep -n MAXMEM_DEFAULT ~/opt/ghidra_12.1.4_PUBLIC/support/analyzeHeadless 2>/dev/null"),
    ("node/java", "ls ~/.local/opt/ 2>/dev/null; java -version 2>&1 | head -2"),
    ("/tmp/bh3", "ls -la /tmp/bh3/ 2>/dev/null"),
    ("Ghidra 残留进程", "ps aux | grep -i '[g]hidra' | wc -l"),
]

cl = paramiko.SSHClient()
cl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    cl.connect(HOST, username=USER, password=PW, timeout=15, banner_timeout=15, auth_timeout=15)
except Exception as e:
    print("[FAIL] 连不上 %s：%s" % (HOST, e))
    sys.exit(1)

print("=== 连接成功：%s ===" % HOST)
for label, cmd in CMDS:
    _, out, err = cl.exec_command(cmd, timeout=60)
    o = out.read().decode("utf-8", "replace").strip()
    e = err.read().decode("utf-8", "replace").strip()
    print("\n--- %s ---" % label)
    print(o if o else "(空)")
    if e and "model name" not in e:
        print("[stderr] %s" % e[:300])
cl.close()
