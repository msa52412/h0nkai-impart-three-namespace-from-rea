# -*- coding: utf-8 -*-
"""
崩坏3 7.0 服务端 v2（.NET 8 + SQLite）一键启动 / 停止

与 launch70.py（v1）的区别：
  * 服务端是 server-v2\\run\\Server.exe
  * **不启动 mongod** —— 存档改成了 SQLite，就在 server-v2\\run\\data\\pemukul.sqlite 里
  * 链路只剩三步：mitmdump(:8891) → nginx(:80) → Server.exe(:443/:8081/:16100)

用法：
  python launch_v2.py start [--host 127.0.0.1] [--no-proxy] [--wait 20]
  python launch_v2.py stop  [--keep-proxy]
  python launch_v2.py status
"""

import argparse
import os
import re
import socket
import subprocess
import sys
import time
import ctypes
from ctypes import wintypes

try:
    import winreg
except ImportError:
    sys.stderr.write("此脚本仅支持 Windows\n")
    sys.exit(2)

# ----------------------------------------------------------------------------
# 路径
#
# ★ 这里原来写死 BASE = r"D:\BH3\7.0"，整个目录一移动就全废。
#   现在改成按脚本位置自动推导，优先级：
#     1) 命令行 --root DIR
#     2) 环境变量 BH3_ROOT
#     3) 脚本位于 <root>\_launch\ 下 -> 取上一级
#     4) 脚本所在目录本身就有 server-v2\ -> 用它
#     5) 兜底：脚本上一级
# ----------------------------------------------------------------------------
BASE = None
V2 = RUN = SERVER_EXE = DB_FILE = None
RUNTIME = NGINX_DIR = NGINX_EXE = None
PROXY_CWD = PROXY_SCRIPT = MITMDUMP_LOCAL = None
STATE_FILE = LOG_DIR = None
NGINX_VHOST = None

MITMDUMP_SYS = r"C:\Program Files\mitmproxy\bin\mitmdump.exe"


def _find_base():
    """猜仓库根目录（见上方优先级说明）。"""
    here = os.path.dirname(os.path.abspath(__file__))
    env = os.environ.get("BH3_ROOT")
    if env:
        return os.path.abspath(env)
    parent = os.path.dirname(here)
    if os.path.isdir(os.path.join(parent, "server-v2")):
        return parent
    if os.path.isdir(os.path.join(here, "server-v2")):
        return here
    return parent


def init_paths(base):
    """按根目录重算所有派生路径。必须在使用任何路径前调用一次。"""
    global BASE, V2, RUN, SERVER_EXE, DB_FILE
    global RUNTIME, NGINX_DIR, NGINX_EXE
    global PROXY_CWD, PROXY_SCRIPT, MITMDUMP_LOCAL
    global STATE_FILE, LOG_DIR, NGINX_VHOST

    BASE = os.path.abspath(base)
    V2 = os.path.join(BASE, "server-v2")
    RUN = os.path.join(V2, "run")
    SERVER_EXE = os.path.join(RUN, "Server.exe")
    DB_FILE = os.path.join(RUN, "data", "pemukul.sqlite")

    RUNTIME = os.path.join(BASE, "runtime")
    NGINX_DIR = os.path.join(RUNTIME, "web", "nginx")
    NGINX_EXE = os.path.join(NGINX_DIR, "nginx.exe")
    PROXY_CWD = os.path.join(RUNTIME, "proxy")
    PROXY_SCRIPT = os.path.join(PROXY_CWD, "proxy.py")
    MITMDUMP_LOCAL = os.path.join(PROXY_CWD, "mitmdump.exe")

    NGINX_VHOST = os.path.join(NGINX_DIR, "conf", "vhosts", "127.0.0.1_80.conf")
    STATE_FILE = os.path.join(BASE, "_launch", ".state_v2.json")
    LOG_DIR = os.path.join(BASE, "_launch", "logs")


PROXY_HOST = "127.0.0.1"
PROXY_PORT = 8891
PROXY_ADDR = "%s:%d" % (PROXY_HOST, PROXY_PORT)

CREATE_NO_WINDOW = 0x08000000
CREATE_NEW_CONSOLE = 0x00000010
DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_BREAKAWAY_FROM_JOB = 0x01000000

INTERNET_SETTINGS = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"

PORTS = [
    ("mitmdump", PROXY_PORT, "中间人（系统代理指向它）"),
    ("nginx", 80, "静态资源 / asset_bundle"),
    ("Server-https", 443, "游戏 Https 入口"),
    ("Server-http", 8081, "游戏 Http 入口"),
]

OK, BAD, WARN, INFO = "[ OK ]", "[FAIL]", "[ -- ]", "[info]"


def out(msg=""):
    print(msg)


def head(msg):
    print()
    print("== %s %s" % (msg, "=" * max(0, 72 - len(msg))))


def port_open(port, host="127.0.0.1", timeout=0.35):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        return s.connect_ex((host, port)) == 0
    except OSError:
        return False
    finally:
        try:
            s.close()
        except OSError:
            pass


def _decode(raw):
    raw = raw or b""
    for enc in ("utf-8", "cp936", "gbk", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", "replace")


def pid_on_port(port):
    try:
        r = subprocess.run(["netstat", "-ano", "-p", "TCP"], capture_output=True, timeout=10)
    except Exception:
        return None
    for line in _decode(r.stdout).splitlines():
        p = line.split()
        if len(p) >= 5 and p[0].upper() == "TCP" and p[3].upper() == "LISTENING":
            if p[1].rsplit(":", 1)[-1] == str(port):
                try:
                    return int(p[4])
                except ValueError:
                    pass
    return None


def exe_path_of_pid(pid):
    if not pid:
        return None
    try:
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        h = k32.OpenProcess(0x1000, False, int(pid))
        if not h:
            return None
        try:
            n = wintypes.DWORD(1024)
            buf = ctypes.create_unicode_buffer(n.value)
            if k32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(n)):
                return buf.value
            return None
        finally:
            k32.CloseHandle(h)
    except Exception:
        return None


def kill_pid(pid, label=""):
    if not pid:
        return False
    try:
        subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True, timeout=15)
        out("  %s 已终止 %s (PID %d)" % (OK, label, pid))
        return True
    except Exception as e:
        out("  %s 终止 %s 失败：%r" % (BAD, label, e))
        return False


# ---------------------------------------------------------------- 系统代理
def read_proxy():
    st = {"ProxyServer": None, "ProxyEnable": 0}
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, INTERNET_SETTINGS)
        try:
            try:
                st["ProxyServer"] = winreg.QueryValueEx(k, "ProxyServer")[0]
            except OSError:
                pass
            try:
                st["ProxyEnable"] = winreg.QueryValueEx(k, "ProxyEnable")[0]
            except OSError:
                pass
        finally:
            winreg.CloseKey(k)
    except OSError:
        pass
    return st


def write_proxy(server, enable):
    k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, INTERNET_SETTINGS, 0, winreg.KEY_SET_VALUE)
    try:
        if server is not None:
            winreg.SetValueEx(k, "ProxyServer", 0, winreg.REG_SZ, server)
        winreg.SetValueEx(k, "ProxyEnable", 0, winreg.REG_DWORD, int(bool(enable)))
    finally:
        winreg.CloseKey(k)
    try:
        for opt in (39, 37):
            ctypes.windll.Wininet.InternetSetOptionW(0, opt, 0, 0)
    except Exception:
        pass


def save_state(patch):
    import json
    st = load_state()
    st.update(patch)
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)


def load_state():
    import json
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def set_system_proxy():
    prev = read_proxy()
    save_state({"proxy_prev": prev})
    write_proxy(PROXY_ADDR, True)
    out("  %s 系统代理已设为 %s（原值已备份，停止时还原）" % (OK, PROXY_ADDR))


def restore_system_proxy():
    prev = load_state().get("proxy_prev")
    if prev:
        write_proxy(prev.get("ProxyServer"), prev.get("ProxyEnable") or 0)
        if (prev.get("ProxyServer") == PROXY_ADDR and (prev.get("ProxyEnable") or 0)
                and not port_open(PROXY_PORT)):
            write_proxy(None, False)
            out("  %s 原值 %s 但 mitmdump 已停（留着会断网），已改为 ProxyEnable=0" % (OK, PROXY_ADDR))
        else:
            out("  %s 系统代理已还原为 %s / Enable=%s"
                % (OK, prev.get("ProxyServer"), prev.get("ProxyEnable")))
        return True
    cur = read_proxy()
    if cur.get("ProxyServer") == PROXY_ADDR:
        write_proxy(None, False)
        out("  %s 未找到备份，已将 ProxyEnable 置 0" % OK)
        return True
    out("  %s 未找到备份，且当前代理不是 %s，已跳过" % (WARN, PROXY_ADDR))
    return False


# ---------------------------------------------------------------- 子进程
_CHILDREN = []


def spawn(name, args, cwd, hidden=True):
    os.makedirs(LOG_DIR, exist_ok=True)
    path = os.path.join(LOG_DIR, "v2_%s.log" % name)
    fh = open(path, "ab")
    base = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP if hidden else CREATE_NEW_CONSOLE
    last = None
    for flags in (base | CREATE_BREAKAWAY_FROM_JOB, base):
        try:
            p = subprocess.Popen(args, cwd=cwd, creationflags=flags,
                                 stdin=subprocess.DEVNULL, stdout=fh,
                                 stderr=subprocess.STDOUT, close_fds=True)
            out("  %s %s 已拉起 (PID %d)，输出 -> %s" % (WARN, name, p.pid, path))
            _CHILDREN.append(p)
            return p
        except FileNotFoundError:
            fh.close()
            out("  %s %s 启动失败：找不到 %s" % (BAD, name, args[0]))
            return None
        except OSError as e:
            last = e
            continue
    fh.close()
    out("  %s %s 启动失败：%s" % (BAD, name, last))
    return None


# ---------------------------------------------------------------- nginx 配置
# nginx 的 vhosts 里写死了仓库绝对路径（root / alias / include 共 7 处），
# 整个目录一移动，nginx 要么起不来要么全部 404。启动前按当前 BASE 就地修正。
_ABS_PATH_RE = re.compile(r"[A-Za-z]:[\\/][^\"';\r\n]*")

# 只认这两类锚点，避免误伤 fastcgi_pass / error_page 之类无关路径
_ANCHORS = ("/runtime/web", "/BH3_Data")


def _rebase(path_str):
    """把 <旧根>/runtime/web... 或 <旧根>/BH3_Data... 改到当前 BASE。"""
    norm = path_str.replace("\\", "/")
    for anchor in _ANCHORS:
        i = norm.find(anchor)
        if i > 0:
            return BASE.replace("\\", "/") + norm[i:]
    return None


def sync_nginx_conf(verbose=True):
    """把 nginx vhosts 里的绝对路径对齐到当前根目录，返回改动处数。"""
    import shutil

    if not os.path.isfile(NGINX_VHOST):
        if verbose:
            out("  %s 没找到 %s，跳过 nginx 路径同步" % (WARN, NGINX_VHOST))
        return 0

    with open(NGINX_VHOST, "rb") as f:
        raw = f.read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    try:
        src = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        if verbose:
            out("  %s %s 不是 UTF-8，跳过同步" % (WARN, NGINX_VHOST))
        return 0

    changes = []

    def _sub(m):
        new = _rebase(m.group(0))
        if new is None or new == m.group(0):
            return m.group(0)
        changes.append((m.group(0), new))
        return new

    dst = _ABS_PATH_RE.sub(_sub, src)
    if not changes:
        if verbose:
            out("  %s nginx vhosts 路径已指向当前目录" % OK)
        return 0

    shutil.copyfile(NGINX_VHOST, NGINX_VHOST + ".bak")
    data = dst.encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    with open(NGINX_VHOST, "wb") as f:
        f.write(data)

    if verbose:
        out("  %s nginx vhosts 已对齐当前目录，改了 %d 处（原文件备份 .bak）"
            % (OK, len(changes)))
        for old, new in changes[:2]:
            out("        %s" % old)
            out("     -> %s" % new)
        if len(changes) > 2:
            out("        ... 另有 %d 处" % (len(changes) - 2))
    return len(changes)


# ---------------------------------------------------------------- 状态
def print_status():
    head("端口状态")
    alive = 0
    for name, port, desc in PORTS:
        pid = pid_on_port(port)
        if pid:
            alive += 1
            out("  %s %-14s :%-5d  PID %-7d # %s" % (OK, name, port, pid, desc))
        else:
            out("  %s %-14s :%-5d  %-11s # %s" % (WARN, name, port, "-", desc))
    out("  %s %-14s :%-5d  %-11s # KCP/UDP，需进游戏才能确认"
        % (WARN, "Server-game", 16100, "-"))

    head("SQLite 存档")
    if os.path.exists(DB_FILE):
        size = os.path.getsize(DB_FILE)
        out("  %s %s  (%.1f KB)" % (OK, DB_FILE, size / 1024.0))
        for ext in ("-wal", "-shm"):
            p = DB_FILE + ext
            if os.path.exists(p):
                out("      + %s  (%.1f KB)" % (os.path.basename(p), os.path.getsize(p) / 1024.0))
    else:
        out("  %s 存档还没生成（首次登录时自动创建）" % WARN)

    head("系统代理")
    cur = read_proxy()
    if cur.get("ProxyEnable") and cur.get("ProxyServer") == PROXY_ADDR:
        out("  %s ProxyEnable=1  ProxyServer=%s  -> 指向本机中间人" % (OK, PROXY_ADDR))
    elif cur.get("ProxyEnable"):
        out("  %s ProxyEnable=1  ProxyServer=%s  -> 不是 %s" % (WARN, cur.get("ProxyServer"), PROXY_ADDR))
    else:
        out("  %s ProxyEnable=0  -> 系统未走代理" % WARN)
    return alive


# ---------------------------------------------------------------- start
def cmd_start(args):
    head("预检")
    fatal = []
    need = [("Server.exe", SERVER_EXE, "file"),
            ("nginx.exe", NGINX_EXE, "file"),
            ("proxy.py", PROXY_SCRIPT, "file"),
            ("config.json", os.path.join(RUN, "config.json"), "file"),
            ("Resources", os.path.join(RUN, "Resources"), "dir")]
    for label, path, kind in need:
        exists = os.path.isdir(path) if kind == "dir" else os.path.isfile(path)
        out("  %s %-14s %s" % (OK if exists else BAD, label, path))
        if not exists:
            fatal.append(label)

    mitm = MITMDUMP_LOCAL if os.path.exists(MITMDUMP_LOCAL) else MITMDUMP_SYS
    out("  %s %-14s %s" % (OK if os.path.exists(mitm) else BAD, "mitmdump.exe", mitm))
    if not os.path.exists(mitm):
        fatal.append("mitmdump.exe")

    if fatal:
        out("")
        out("  %s 缺少关键组件，已中止：%s" % (BAD, ", ".join(fatal)))
        return 1

    head("① 服务端配置 Gameserver.Host")
    cur_host = read_host()
    if args.host in ("keep", "auto", ""):
        out("  %s 沿用当前值 %s（未改 config）" % (WARN, cur_host))
    else:
        old = write_host(args.host)
        if old == args.host:
            out("  %s 已是 %s，无需修改" % (OK, args.host))
        else:
            out("  %s %s -> %s（原文件备份 config.json.bak）" % (OK, old, args.host))

    head("② 系统代理")
    if args.no_proxy:
        out("  %s --no-proxy：跳过" % WARN)
    else:
        set_system_proxy()

    head("③ 中间人 mitmdump（:%d）" % PROXY_PORT)
    if port_open(PROXY_PORT):
        out("  %s 端口 %d 已被占用（PID %s），复用" % (OK, PROXY_PORT, pid_on_port(PROXY_PORT)))
    else:
        spawn("mitmdump", [mitm, "-p", str(PROXY_PORT), "-s", PROXY_SCRIPT], PROXY_CWD)

    head("④ nginx（:80）")
    sync_nginx_conf()
    if port_open(80):
        out("  %s 端口 80 已被占用（PID %s），复用" % (OK, pid_on_port(80)))
    else:
        spawn("nginx", [NGINX_EXE], NGINX_DIR)

    head("⑤ Server.exe（:443 / :8081）")
    if port_open(443) or port_open(8081):
        pid = pid_on_port(443) or pid_on_port(8081)
        cur = exe_path_of_pid(pid)
        if cur and os.path.normcase(cur) != os.path.normcase(SERVER_EXE):
            out("  %s 443/8081 被另一套服务端占用，不能复用：" % BAD)
            out("        PID  %s" % pid)
            out("        正在跑  %s" % cur)
            out("        本脚本要  %s" % SERVER_EXE)
            out("")
            out("  443/8081 只能跑 server-v2\\run\\Server.exe 这一套。")
            out("  若是残留的服务端进程（v1 已于 2026-10-25 删除），先停掉它。")
            return 1
        out("  %s 已是本版在跑（PID %s），不重复启动" % (OK, pid))
    else:
        spawn("Server", [SERVER_EXE], RUN, hidden=not args.show_console)

    head("⑥ 等待就绪")
    expect = [(PROXY_PORT, "mitmdump"), (80, "nginx"),
              (443, "Server-https"), (8081, "Server-http")]
    pending = dict(expect)
    deadline = time.time() + args.wait
    while pending and time.time() < deadline:
        for p in list(pending.keys()):
            if port_open(p):
                out("  %s %-18s :%-5d 就绪" % (OK, pending.pop(p), p))
        if pending:
            time.sleep(0.4)
    for p, n in pending.items():
        out("  %s %-18s :%-5d 在 %ds 内未就绪（看 %s\\v2_*.log）" % (WARN, n, p, args.wait, LOG_DIR))

    print_status()

    head("完成")
    out("  客户端连：%s" % read_host())
    out("  停止：双击「停止服务端v2.bat」")
    out("")
    return 0


def read_host():
    import json
    try:
        with open(os.path.join(RUN, "config.json"), encoding="utf-8-sig") as f:
            return json.load(f).get("Gameserver", {}).get("Host", "?")
    except Exception:
        return "?"


def write_host(new_host):
    """改写 config.json 里的 Gameserver.Host，返回原值。保留原文件格式（缩进 2）。"""
    import json
    import shutil
    path = os.path.join(RUN, "config.json")
    with open(path, encoding="utf-8-sig") as f:
        cfg = json.load(f)
    old = cfg.get("Gameserver", {}).get("Host", "")
    if old != new_host:
        shutil.copyfile(path, path + ".bak")
        cfg.setdefault("Gameserver", {})["Host"] = new_host
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    return old


# ---------------------------------------------------------------- stop
def cmd_stop(args):
    head("停止 v2 栈")
    pid = pid_on_port(443) or pid_on_port(8081)
    if pid:
        kill_pid(pid, "Server.exe")
    else:
        out("  %s Server.exe 未在运行" % WARN)

    if pid_on_port(80):
        subprocess.run([NGINX_EXE, "-s", "stop"], cwd=NGINX_DIR, capture_output=True, timeout=20)
        time.sleep(0.6)
        if pid_on_port(80):
            kill_pid(pid_on_port(80), "nginx")
        else:
            out("  %s nginx 已停止" % OK)
    else:
        out("  %s nginx 未在运行" % WARN)

    if pid_on_port(PROXY_PORT):
        kill_pid(pid_on_port(PROXY_PORT), "mitmdump")
    else:
        out("  %s mitmdump 未在运行" % WARN)

    head("系统代理")
    if args.keep_proxy:
        out("  %s --keep-proxy：保留不动" % WARN)
    else:
        restore_system_proxy()
    out("")
    return 0


# ---------------------------------------------------------------- paths
def cmd_paths(args):
    """只做路径体检 + nginx 配置同步，不碰任何进程。

    目录搬家后先跑这个，能立刻看出哪个组件没跟上。
    """
    head("根目录")
    out("  %s" % BASE)

    head("关键组件")
    need = [("Server.exe", SERVER_EXE),
            ("nginx.exe", NGINX_EXE),
            ("proxy.py", PROXY_SCRIPT),
            ("config.json", os.path.join(RUN, "config.json")),
            ("nginx vhost", NGINX_VHOST)]
    missing = 0
    for label, path in need:
        ok = os.path.exists(path)
        if not ok:
            missing += 1
        out("  %s %-13s %s" % (OK if ok else BAD, label, path))

    head("nginx vhosts 路径同步")
    sync_nginx_conf()

    out("")
    if missing:
        out("  %s 有 %d 个组件不在当前根目录下，检查是否只搬了一半" % (BAD, missing))
        return 1
    out("  %s 路径全部就位" % OK)
    out("")
    return 0


# ---------------------------------------------------------------- main
def main():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--root", default=None, metavar="DIR",
                        help="仓库根目录；默认按脚本位置自动推导")

    ap = argparse.ArgumentParser(prog="launch_v2")
    sub = ap.add_subparsers(dest="cmd")

    ps = sub.add_parser("start", parents=[common])
    ps.add_argument("--host", default="keep")
    ps.add_argument("--no-proxy", action="store_true")
    ps.add_argument("--show-console", action="store_true", help="显示服务端控制台窗口")
    ps.add_argument("--wait", type=int, default=20)

    pd = sub.add_parser("stop", parents=[common])
    pd.add_argument("--keep-proxy", action="store_true")

    sub.add_parser("status", parents=[common])
    sub.add_parser("paths", parents=[common], help="只检查路径并同步 nginx 配置，不启动任何服务")

    args = ap.parse_args()
    if args.cmd is None:
        args.cmd = "start"
        args.host = "keep"
        args.no_proxy = False
        args.show_console = False
        args.wait = 20

    init_paths(getattr(args, "root", None) or _find_base())

    if args.cmd == "start":
        return cmd_start(args)
    if args.cmd == "stop":
        return cmd_stop(args)
    if args.cmd == "paths":
        return cmd_paths(args)
    print_status()
    return 0


if __name__ == "__main__":
    sys.exit(main())
