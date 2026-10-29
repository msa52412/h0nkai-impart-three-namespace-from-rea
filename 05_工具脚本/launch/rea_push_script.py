# -*- coding: utf-8 -*-
"""把本地脚本推到远端 NAS（rea_run_analysis.sh / rea_probe.py）。"""
import sys
import paramiko

HOST = sys.argv[1] if len(sys.argv) > 1 else "192.168.0.105"
USER, PW = "nas", "mt#win7"
BASE = r"D:\BH3\7.0\_launch"

PUSH = [
    ("rea_run_analysis.sh", "/home/nas/bh3_run_analysis.sh", 0o755),
]

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, username=USER, password=PW, timeout=15)
sftp = cli.open_sftp()
for name, remote, mode in PUSH:
    local = BASE + "\\" + name
    print("上传 %s -> %s" % (name, remote))
    sftp.put(local, remote)
    sftp.chmod(remote, mode)
sftp.close()
_, out, _ = cli.exec_command("ls -la /home/nas/bh3_run_analysis.sh; sh -n /home/nas/bh3_run_analysis.sh && echo '[OK] 语法检查通过'")
print(out.read().decode())
cli.close()
