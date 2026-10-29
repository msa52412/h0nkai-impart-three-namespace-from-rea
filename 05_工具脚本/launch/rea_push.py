# -*- coding: utf-8 -*-
"""把崩坏3 的 IL2CPP 产物推到远端 Linux NAS，供 rea 逆向。

为什么需要这一步
----------------
rea 服务跑在 192.168.0.104（Linux NAS）上，它只能看见那台机器的文件系统，
D 盘对它不可见（/mnt 和 /media 都是空的）。所以先把要分析的文件推过去。

推两个文件：
  UserAssembly.dll     190 MB  IL2CPP 原生代码（崩3 不叫 GameAssembly.dll）
  global-metadata.dat   56 MB  IL2CPP 元数据（类型/方法/字符串池）

用法：
  python _launch/rea_push.py            # 全推
  python _launch/rea_push.py --only ua  # 只推 dll
"""

import argparse
import os
import sys
import time

import paramiko

# 2026-10-21：NAS 升级后换了机器（192.168.0.104 -> 192.168.0.105），凭据不变。
# 目录必须放磁盘 /home/nas/bh3，不能放 /tmp —— 新机器的 /tmp 是 tmpfs（RAM 盘，6.1G），
# 190MB 的目标加 Ghidra 的分析产物会把内存吃掉，而我们恰恰需要内存来分析。
HOST = "192.168.0.105"
USER = "nas"
PASS = "mt#win7"
REMOTE_DIR = "/home/nas/bh3"

BASE = r"D:\BH3\7.0"
FILES = {
    "ua": (os.path.join(BASE, "BH3_Data", "Native", "UserAssembly.dll"), "UserAssembly.dll"),
    "meta": (os.path.join(BASE, "BH3_Data", "Managed", "Metadata", "global-metadata.dat"), "global-metadata.dat"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=list(FILES), help="只推一个")
    ap.add_argument("--host", default=HOST)
    args = ap.parse_args()

    keys = [args.only] if args.only else list(FILES)

    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"连接 {args.host} ...")
    cli.connect(args.host, username=USER, password=PASS, timeout=15)
    print("  [OK] 已连接")

    stdin, stdout, stderr = cli.exec_command(f"mkdir -p {REMOTE_DIR} && df -h {REMOTE_DIR} | tail -1")
    print("  远端空间:", stdout.read().decode().strip())

    sftp = cli.open_sftp()
    for k in keys:
        local, name = FILES[k]
        if not os.path.isfile(local):
            print(f"  [SKIP] 本地不存在: {local}")
            continue
        size = os.path.getsize(local)
        remote = f"{REMOTE_DIR}/{name}"
        print(f"上传 {name}  {size/1048576:.1f} MB -> {remote}")

        state = {"t": time.time(), "last": -1}

        def cb(done, total, _size=size, _state=state):
            pct = int(done * 100 / total) if total else 0
            if pct // 10 != _state["last"] // 10:
                _state["last"] = pct
                el = time.time() - _state["t"]
                print(f"    {pct:3d}%  {done/1048576:6.1f} MB  {el:5.1f}s")

        t0 = time.time()
        sftp.put(local, remote, callback=cb)
        print(f"  [OK] {name} 用时 {time.time()-t0:.1f}s")

    sftp.close()
    stdin, stdout, stderr = cli.exec_command(f"ls -la {REMOTE_DIR}")
    print("\n远端目录：")
    print(stdout.read().decode())
    cli.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
