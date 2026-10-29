# -*- coding: utf-8 -*-
"""只重启 Server.exe，不动 nginx / mitmdump / 系统代理。

为什么不用 launch_v2.py stop
---------------------------
`launch_v2.py stop` 会把整条链路都停掉（nginx :80、mitmdump :8891），
最后还会 restore_system_proxy() 改回系统代理设置。
改一次服务端代码不该把整条链都拆了重建。

本脚本复用 launch_v2 自己的 spawn()（同样的 DETACHED_PROCESS +
CREATE_BREAKAWAY_FROM_JOB + 日志重定向到 _launch/logs/v2_Server.log），
只对 Server.exe 一个进程做停/起。

用法:
    python restart_server.py             # 停 → 起
    python restart_server.py --only-stop # 只停（编译前用）
    python restart_server.py --only-start
    python restart_server.py --status
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import launch_v2 as L  # noqa: E402

# launch_v2 的路径现在是运行时推导的，import 之后必须初始化一次，
# 否则 L.SERVER_EXE / L.RUN 都是 None。
L.init_paths(L._find_base())


def server_pid():
    """按 443 / 8081 端口找 Server.exe。"""
    for port in (443, 8081):
        pid = L.pid_on_port(port)
        if pid:
            return pid
    return None


def do_status():
    pid = server_pid()
    if not pid:
        print("Server.exe 未在运行")
        return 1
    print("Server.exe PID %s  %s" % (pid, L.exe_path_of_pid(pid)))
    return 0


def do_stop():
    pid = server_pid()
    if not pid:
        print("Server.exe 未在运行，跳过")
        return 0
    print("停止 Server.exe PID %s …" % pid)
    L.kill_pid(pid, "Server.exe")
    for _ in range(40):
        if not server_pid():
            print("已停止")
            return 0
        time.sleep(0.25)
    print("✗ 20 秒内没停下来")
    return 1


def do_start():
    if server_pid():
        print("Server.exe 已在运行（PID %s），不重复启动" % server_pid())
        return 0
    print("启动 Server.exe …")
    L.spawn("Server", [L.SERVER_EXE], L.RUN, hidden=True)
    for _ in range(60):
        pid = server_pid()
        if pid:
            print("已拉起 PID %s，日志 -> %s"
                  % (pid, os.path.join(L.LOG_DIR, "v2_Server.log")))
            return 0
        time.sleep(0.5)
    print("✗ 30 秒内没起来，看日志")
    return 1


def main():
    a = sys.argv[1:]
    if "--status" in a:
        return do_status()
    if "--only-stop" in a:
        return do_stop()
    if "--only-start" in a:
        return do_start()
    rc = do_stop()
    if rc != 0:
        return rc
    time.sleep(0.8)
    return do_start()


if __name__ == "__main__":
    sys.exit(main())
