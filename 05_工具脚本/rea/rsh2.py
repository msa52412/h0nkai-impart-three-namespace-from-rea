#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rsh2.py — 双机 SSH 统一入口（104 与 105）。
104: 密钥 ~/.ssh/rea_remote
105: 密码 mt#win7，已装同一把公钥，优先也走密钥
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_pylibs"))
import paramiko

KEY = os.path.expanduser("~/.ssh/rea_remote")

HOSTS = {
    "104": dict(host="192.168.0.104", user="nas", pwd="mt#win7"),
    "105": dict(host="192.168.0.105", user="nas", pwd="mt#win7"),
}


def conn(which="104", timeout=25):
    c = HOSTS[str(which)]
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    kw = dict(hostname=c["host"], port=22, username=c["user"], timeout=timeout,
              banner_timeout=30, auth_timeout=30,
              allow_agent=False, look_for_keys=False, password=c["pwd"])
    if os.path.exists(KEY):
        kw["key_filename"] = KEY
    cli.connect(**kw)
    return cli


def run(cli, cmd, timeout=600):
    si, so, se = cli.exec_command(cmd, timeout=timeout)
    out = so.read().decode("utf-8", "replace")
    err = se.read().decode("utf-8", "replace")
    rc = so.channel.recv_exit_status()
    return rc, out, err


def sh(which, cmd, timeout=600, tail=40, quiet=False):
    cli = conn(which)
    try:
        rc, o, e = run(cli, cmd, timeout)
    finally:
        cli.close()
    if not quiet:
        print("=== [%s] rc=%d | %s" % (which, rc, cmd.replace("\n", " ")[:100]))
        if o.strip():
            for ln in o.rstrip().splitlines()[-tail:]:
                print("  " + ln)
        if e.strip():
            for ln in e.strip().splitlines()[-12:]:
                print("  ! " + ln)
        print()
    return rc, o, e


def put(which, local, remote):
    cli = conn(which)
    try:
        sf = cli.open_sftp()
        try:
            sf.put(local, remote)
        finally:
            sf.close()
    finally:
        cli.close()


def get(which, remote, local):
    cli = conn(which)
    try:
        sf = cli.open_sftp()
        try:
            sf.get(remote, local)
        finally:
            sf.close()
    finally:
        cli.close()


if __name__ == "__main__":
    w = sys.argv[1] if len(sys.argv) > 1 else "105"
    cmdline = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "echo ok; hostname"
    sh(w, cmdline)
