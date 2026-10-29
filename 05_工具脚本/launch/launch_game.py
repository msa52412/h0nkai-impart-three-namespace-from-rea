# -*- coding: utf-8 -*-
"""launch_game.py —— 一键启动：服务端（按需）+ 客户端 + 刻晴补丁

为什么需要这个脚本
------------------
客户端**不能改文件**（STRUCTURE.md：改了签名就过不了），
所以刻晴的隐藏只能在运行时用内存补丁绕过（见 tools/keqing_visible.py）。
内存补丁的生命周期 = 进程生命周期，**每次启动游戏都要重新打**。

以前的做法是「先开游戏 → 再手动跑 wait」，两步而且容易忘。
这里把三步合成一次：

    ① 服务端没起 → 调 launch_v2.py start（含代理设置）
    ② 拉起 BH3.exe
    ③ 等 UserAssembly.dll 加载好 → 打补丁

「等」是躲不掉的：进程没起来就没有内存可写。但对使用者来说只是双击一次，
不需要再单独跑一个 wait 命令。

用法
----
    python launch_game.py               服务端按需 + 启动游戏 + 打补丁
    python launch_game.py --no-server   不碰服务端，只启动游戏 + 打补丁
    python launch_game.py --no-launch   不启动游戏，只对已运行的进程打补丁
    python launch_game.py --no-patch    只启动，不打补丁
    python launch_game.py --avatar 316  换一个要放出来的角色
"""
import os
import socket
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                 # D:\BH3\7.0
TOOLS = os.path.join(ROOT, "tools")
GAME_EXE = os.path.join(ROOT, "BH3.exe")
LAUNCH_V2 = os.path.join(HERE, "launch_v2.py")

sys.path.insert(0, TOOLS)
try:
    import keqing_visible as K
except Exception as e:                        # noqa: BLE001
    print("[!] 无法导入 tools\\keqing_visible.py：%s" % e)
    sys.exit(1)

DEFAULT_AVATAR = 2001
WAIT_SECONDS = 180


def out(msg=""):
    print(msg)
    sys.stdout.flush()


def port_open(port, host="127.0.0.1", timeout=0.4):
    s = socket.socket()
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        return True
    except Exception:                         # noqa: BLE001
        return False
    finally:
        s.close()


def server_ready():
    """443 = Server.exe TLS，8081 = HTTP。任一个在听就算起来了。"""
    return port_open(443) or port_open(8081)


def start_server():
    if not os.path.exists(LAUNCH_V2):
        out("[!] 找不到启动器：%s" % LAUNCH_V2)
        return False
    out("① 服务端没在跑，开始启动（mitmdump → nginx → Server.exe）...")
    out("   这一步会设置系统代理，需要一点时间。")
    py = sys.executable
    rc = subprocess.call([py, LAUNCH_V2, "start", "--root", ROOT + os.sep + "."],
                         cwd=ROOT)
    if rc != 0:
        out("[!] 服务端启动失败（exit=%d），日志在 _launch\\logs\\v2_*.log" % rc)
        return False
    out("   服务端已就绪。")
    return True


def game_running():
    return K.find_pid() is not None


def launch_game():
    if not os.path.exists(GAME_EXE):
        out("[!] 找不到客户端：%s" % GAME_EXE)
        return False
    out("② 启动客户端：%s" % GAME_EXE)
    try:
        subprocess.Popen([GAME_EXE], cwd=ROOT)
    except Exception as e:                    # noqa: BLE001
        out("[!] 启动失败：%s" % e)
        return False
    return True


def main():
    argv = sys.argv[1:]
    no_server = "--no-server" in argv
    no_launch = "--no-launch" in argv
    no_patch = "--no-patch" in argv
    avatar = DEFAULT_AVATAR
    if "--avatar" in argv:
        avatar = int(argv[argv.index("--avatar") + 1], 0)

    out("=" * 62)
    out("  BH3 一键启动（含刻晴补丁 avatarID=%d）" % avatar)
    out("=" * 62)
    out("根目录：%s" % ROOT)
    out()

    # ---------- ① 服务端 ----------
    if no_server:
        out("① 跳过服务端检查（--no-server）")
    elif server_ready():
        out("① 服务端已在运行（443/8081 有监听），跳过。")
    else:
        if not start_server():
            out()
            out("启动中止：客户端连不上服务端，先起游戏没有意义。")
            return 1

    # ---------- ② 客户端 ----------
    if no_launch:
        out("② 跳过启动（--no-launch）")
        if not game_running():
            out("[!] 但 %s 没在运行，没东西可打补丁。" % K.PROC_NAME)
            return 1
    elif game_running():
        out("② 客户端已在运行，不重复启动。")
    else:
        if not launch_game():
            return 1

    # ---------- ③ 补丁 ----------
    if no_patch:
        out("③ 跳过补丁（--no-patch）")
        out()
        out("完成。")
        return 0

    out("③ 等 UserAssembly.dll 加载，然后打补丁（最多 %d 秒）..." % WAIT_SECONDS)
    out()
    rc = K.cmd_wait(WAIT_SECONDS, avatar)
    out()
    if rc == 0:
        out("=" * 62)
        out("  完成。刻晴应当在角色列表里。")
        out("=" * 62)
        out("提示：补丁只在本次进程有效。下次启动直接双击本脚本即可，")
        out("      不需要再单独跑 wait。")
    else:
        out("=" * 62)
        out("  补丁没打上，看上面的原因。")
        out("=" * 62)
    return rc


if __name__ == "__main__":
    sys.exit(main())
