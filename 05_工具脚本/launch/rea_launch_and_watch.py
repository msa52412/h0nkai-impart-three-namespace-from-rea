# -*- coding: utf-8 -*-
"""在远端 NAS 后台启动 rea 全量分析，并轮询进度。"""
import sys
import time
import paramiko

HOST = sys.argv[1] if len(sys.argv) > 1 else "192.168.0.105"
USER, PW = "nas", "mt#win7"
ROUNDS = int(sys.argv[2]) if len(sys.argv) > 2 else 6
INTERVAL = int(sys.argv[3]) if len(sys.argv) > 3 else 90

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, username=USER, password=PW, timeout=15)


def run(cmd, timeout=60):
    _, out, err = cli.exec_command(cmd, timeout=timeout)
    return out.read().decode("utf-8", "replace").strip(), err.read().decode("utf-8", "replace").strip()


# 已经在跑就别重复起
o, _ = run("pgrep -af 'rea.*inspect' | head -3")
if o:
    print("[已在运行]\n" + o)
else:
    o, e = run(
        "cd $HOME && rm -f bh3_run.log && "
        "nohup sh bh3_run_analysis.sh > bh3_run.log 2>&1 & "
        "echo started pid=$!"
    )
    print("[启动] " + (o or e))

for i in range(ROUNDS):
    time.sleep(INTERVAL)
    o, _ = run(
        "echo '--- 运行中? ---'; pgrep -af 'ghidra|Ghidra-Headless|rea ' | head -3; "
        "echo '--- 内存 ---'; free -m | awk '/Mem:/{print $7\" MB avail}\'; "
        "echo '--- 日志尾 ---'; tail -c 800 $HOME/bh3_run.log 2>/dev/null; "
        "echo; echo '--- 结果? ---'; ls -la $HOME/bh3_work/ 2>/dev/null"
    )
    print("\n===== 第 %d 次检查 (%s) =====" % (i + 1, time.strftime("%H:%M:%S")))
    print(o)
    if "rea_result.json" in o and "No such" not in o:
        print("\n[完成] 结果文件已生成")
        break
cli.close()
