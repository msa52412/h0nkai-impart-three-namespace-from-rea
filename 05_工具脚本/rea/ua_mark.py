# -*- coding: utf-8 -*-
"""UserAssembly.dll 惰性标记：改嵌入 PDB 路径里的一个字符

这个字节只用于「证明签名校验是否被绕过」：
它完全不参与程序逻辑（PDB 路径只在附加调试器时才被读取），
所以如果游戏能正常启动并进入，就说明签名校验确实失效了，
同时也没有因为是「改了有意义的代码」而引入干扰变量。

用法
----
    python ua_mark.py status
    python ua_mark.py mark
    python ua_mark.py unmark
"""
import sys, os, shutil

P = r"D:\BH3\7.0\BH3_Data\Native\UserAssembly.dll"
BAK = P + ".bak_uv"
NEEDLE = b"UserAssembly.pdb"
MARKED = b"UserAssembly.qdb"


def read(p=P):
    with open(p, "rb") as f:
        return f.read()


def find_off(d):
    return d.find(NEEDLE)


def status():
    d = read()
    print("UserAssembly.dll  %d B" % len(d))
    i = find_off(d)
    j = d.find(MARKED)
    if i >= 0:
        print("  标记状态: 原版 (%r @ %#x)" % (NEEDLE, i))
    elif j >= 0:
        print("  标记状态: 已打标记 (%r @ %#x)" % (MARKED, j))
    else:
        print("  标记状态: 找不到锚点字符串！")
    print("  备份: %s" % ("存在 %d B" % os.path.getsize(BAK) if os.path.exists(BAK) else "无"))


def mark():
    d = bytearray(read())
    i = find_off(d)
    if i < 0:
        if d.find(MARKED) >= 0:
            print("已经打过标记。"); return
        print("找不到锚点 'UserAssembly.pdb'，放弃"); return
    if not os.path.exists(BAK):
        shutil.copy2(P, BAK)
        print("[+] 已备份 -> %s" % BAK)
    d[i + len(b"UserAssembly.")] = ord("q")
    with open(P, "wb") as f:
        f.write(d)
    print("[+] 已打标记: UserAssembly.pdb -> UserAssembly.qdb")
    status()


def unmark():
    if not os.path.exists(BAK):
        print("没有备份，无法还原"); return
    shutil.copy2(BAK, P)
    print("[+] 已从备份还原")
    status()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"status": status, "mark": mark, "unmark": unmark}[cmd]()
