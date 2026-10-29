#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rsh.py — 远端 192.168.0.104 的 SSH/SFTP 便捷封装"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_pylibs"))
import paramiko

HOST = "192.168.0.104"
USER = "nas"
PWD  = "mt#win7"

def conn(timeout=20):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, 22, USER, PWD, timeout=timeout,
              allow_agent=False, look_for_keys=False)
    return c

def run(cli, cmd, timeout=600):
    """执行远端命令，返回 (rc, stdout, stderr)"""
    si, so, se = cli.exec_command(cmd, timeout=timeout)
    out = so.read().decode("utf-8", "replace")
    err = se.read().decode("utf-8", "replace")
    rc = so.channel.recv_exit_status()
    return rc, out, err

def sftp_put(cli, local, remote):
    sf = cli.open_sftp()
    try:
        d = os.path.dirname(remote)
        try:
            sf.stat(d)
        except IOError:
            sf.mkdir(d)
        sf.put(local, remote)
    finally:
        sf.close()

def sftp_get(cli, remote, local):
    sf = cli.open_sftp()
    try:
        sf.get(remote, local)
    finally:
        sf.close()

if __name__ == "__main__":
    cli = conn()
    rc, o, e = run(cli, sys.argv[1] if len(sys.argv) > 1 else "echo ok")
    print("rc=", rc)
    print(o)
    if e.strip():
        print("STDERR:", e[:2000])
    cli.close()
