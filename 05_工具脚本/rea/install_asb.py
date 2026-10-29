# -*- coding: utf-8 -*-
"""把 patch_asb 下的补丁包装入客户端，自动备份原件；支持 restore / status"""
import os, shutil, sys, hashlib

ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
PATCH_DIR = r"D:/Carol-start/_rea/patch_asb"

def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

def install(name):
    src = os.path.join(PATCH_DIR, name)
    dst = os.path.join(ASB, name)
    bak = dst + ".orig"
    assert os.path.exists(src), "补丁不存在: " + src
    assert os.path.exists(dst), "客户端原件不存在: " + dst
    if not os.path.exists(bak):
        shutil.copy2(dst, bak)
        print("已备份原件 ->", bak, md5(bak))
    else:
        print("备份已存在:", bak, md5(bak))
    sa, sb = os.path.getsize(src), os.path.getsize(dst)
    assert sa == sb, "长度不一致 %d vs %d" % (sa, sb)
    shutil.copy2(src, dst)
    print("已装入补丁 ->", dst)
    print("  现在 md5 =", md5(dst), " 长度 =", os.path.getsize(dst))
    print("  原始 md5 =", os.path.basename(name).replace(".wmv", ""))

def restore(name):
    dst = os.path.join(ASB, name)
    bak = dst + ".orig"
    assert os.path.exists(bak), "无备份: " + bak
    shutil.copy2(bak, dst)
    print("已还原 ->", dst, md5(dst))

def status(name):
    dst = os.path.join(ASB, name)
    bak = dst + ".orig"
    print("目标 :", dst)
    print("  存在:", os.path.exists(dst), " md5:", md5(dst) if os.path.exists(dst) else "-")
    print("备份 :", bak)
    print("  存在:", os.path.exists(bak), " md5:", md5(bak) if os.path.exists(bak) else "-")
    want = os.path.basename(name).replace(".wmv", "")
    cur = md5(dst) if os.path.exists(dst) else None
    print("  与原名一致(=原版):", cur == want)

if __name__ == "__main__":
    NAME = "f65865df27ea6a9e58bf8f1f3b01bdcd.wmv"
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"install": install, "restore": restore, "status": status}[cmd](NAME)
