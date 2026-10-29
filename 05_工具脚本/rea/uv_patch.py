# -*- coding: utf-8 -*-
"""UnityPlayer.dll 签名校验旁路补丁

原理
----
UnityPlayer.dll 内唯一的 WinVerifyTrust 导入跳板位于 VA 0x18133FBDA
（文件偏移 0x133F1DA）：

    FF 25 48 05 19 00   jmp qword ptr [rip+0x190548]
                        -> 目标 = 0x18133FBDA+6+0x190548 = 0x1814D0128
                           = wintrust.dll!WinVerifyTrust 的 IAT 槽

把它改成 `31 C0 C3 90 90 90`（xor eax,eax; ret; nop*3），
则任何调用 WinVerifyTrust 的代码都会立即拿到 0 = ERROR_SUCCESS（签名有效）。

调用链（实测）：
    IL2CPP 加载区 0x180E9FF..0x180EA0C
      -> 0x18097E060  (277 KB 混淆巨函数)
        -> 0x181319580 (无静态调用者，经函数指针调用)
          -> 0x181326B50
            -> 0x181326880 (WinVerifyTrust 封装，返回 bool)
              -> 0x18133FBDA (导入跳板)

用法
----
    python uv_patch.py status
    python uv_patch.py apply
    python uv_patch.py revert
"""
import sys, os, shutil, struct

P = r"D:\BH3\7.0\UnityPlayer.dll"
BAK = P + ".bak_uv"
OFF_THUNK = 0x133F1DA
ORIG = bytes.fromhex("FF254805 1900".replace(" ", ""))
PATCH = bytes.fromhex("31C0C390 9090".replace(" ", ""))


def read(p=P):
    with open(p, "rb") as f:
        return f.read()


def status():
    d = read()
    cur = d[OFF_THUNK:OFF_THUNK + 6]
    print("UnityPlayer.dll  %d B" % len(d))
    print("  跳板 %#x 当前字节: %s" % (OFF_THUNK, cur.hex(" ")))
    if cur == ORIG:
        print("  状态: 原版（校验未旁路）")
    elif cur == PATCH:
        print("  状态: 已打补丁（WinVerifyTrust 恒返回 0）")
    else:
        print("  状态: 未知字节！")
    print("  备份: %s" % ("存在 %d B" % os.path.getsize(BAK) if os.path.exists(BAK) else "无"))


def apply():
    d = bytearray(read())
    cur = bytes(d[OFF_THUNK:OFF_THUNK + 6])
    if cur == PATCH:
        print("已经是补丁状态，无需重复。")
        return
    if cur != ORIG:
        print("原字节不匹配，拒绝修改：%s" % cur.hex(" "))
        return
    if not os.path.exists(BAK):
        shutil.copy2(P, BAK)
        print("[+] 已备份 -> %s" % BAK)
    d[OFF_THUNK:OFF_THUNK + 6] = PATCH
    with open(P, "wb") as f:
        f.write(d)
    print("[+] 已写入补丁")
    verify()


def revert():
    if not os.path.exists(BAK):
        print("没有备份，无法回滚")
        return
    shutil.copy2(BAK, P)
    print("[+] 已从备份还原 %s" % BAK)
    verify()


def verify():
    d = read()
    cur = d[OFF_THUNK:OFF_THUNK + 6]
    # PE 基本校验
    ok = d[:2] == b"MZ"
    pe = struct.unpack_from("<I", d, 0x3C)[0]
    ok = ok and d[pe:pe + 4] == b"PE\0\0"
    print("  复核: 跳板=%s  PE头=%s  大小=%d" % (cur.hex(" "), "OK" if ok else "损坏", len(d)))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"status": status, "apply": apply, "revert": revert}[cmd]()
