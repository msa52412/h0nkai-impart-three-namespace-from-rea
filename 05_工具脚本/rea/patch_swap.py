# -*- coding: utf-8 -*-
r"""改档替换实验工具 —— 一键替换 / 恢复客户端 metadata
   用法:
     python patch_swap.py install work_metadata_patched.dat   # 替换(自动备份原件+同步pkg_version)
     python patch_swap.py install xxx.dat --no-sync           # 替换但【不动清单】→ 测清单是否被强制校验
     python patch_swap.py restore                             # 恢复原版
     python patch_swap.py status                              # 查看当前状态
   设计原则：NAS 原件(Z:)永不动；操作的是 D:\BH3\7.0 本地客户端（文档所述实际运行目录）"""
import hashlib
import json
import os
import shutil
import sys

# 实际客户端位置（按 客户端逆向地图.md：客户端 = D:\BH3\7.0\BH3.exe）
CLIENT_DIR = r"D:\BH3\7.0"
META_REL = r"BH3_Data\Managed\Metadata\global-metadata.dat"
PKG = os.path.join(CLIENT_DIR, "pkg_version")
META = os.path.join(CLIENT_DIR, META_REL)
BAK = META + ".orig"


def md5f(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def status():
    if not os.path.exists(META):
        print("客户端不存在:", META)
        return
    cur = md5f(META)
    print("当前 metadata md5:", cur)
    if os.path.exists(BAK):
        print("备份存在, 原 md5:", md5f(BAK), "(已替换)" if cur != md5f(BAK) else "(未替换)")
    else:
        print("无备份(原版状态)")
    # pkg_version 里记录的期望值
    if os.path.exists(PKG):
        for ln in open(PKG, encoding="utf-8", errors="replace"):
            if "global-metadata" in ln:
                e = json.loads(ln)
                print("pkg_version 期望 md5:", e["md5"], " 匹配:", e["md5"].upper() == cur)


def install(src, sync=True):
    if not os.path.exists(src):
        sys.exit("补丁文件不存在: " + src)
    if not os.path.exists(META):
        sys.exit("客户端不存在: " + META)
    if not os.path.exists(BAK):
        shutil.copy2(META, BAK)
        print("已备份原件 →", BAK)
    shutil.copy2(src, META)
    nmd5 = md5f(META)
    print("已替换, 新 md5:", nmd5)
    # 同步 pkg_version（若客户端本地校验清单）
    if os.path.exists(PKG) and sync:
        lines = open(PKG, encoding="utf-8").read().splitlines()
        out = []
        changed = 0
        for ln in lines:
            if "global-metadata" in ln and ln.strip():
                e = json.loads(ln)
                e["md5"] = nmd5
                e["fileSize"] = os.path.getsize(META)
                out.append(json.dumps(e, separators=(",", ":")))
                changed += 1
            else:
                out.append(ln)
        with open(PKG, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(out) + "\n")
        print("pkg_version 已同步 (%d 条)" % changed)
    print("完成。启动客户端观察是否正常加载。")


def restore():
    if not os.path.exists(BAK):
        sys.exit("无备份可恢复")
    shutil.copy2(BAK, META)
    omd5 = md5f(META)
    print("已恢复原版, md5:", omd5)
    if os.path.exists(PKG):
        lines = open(PKG, encoding="utf-8").read().splitlines()
        out = []
        for ln in lines:
            if "global-metadata" in ln and ln.strip():
                e = json.loads(ln)
                e["md5"] = omd5
                e["fileSize"] = os.path.getsize(META)
                out.append(json.dumps(e, separators=(",", ":")))
            else:
                out.append(ln)
        with open(PKG, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(out) + "\n")
        print("pkg_version 已还原")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "status":
        status()
    elif cmd == "install" and len(sys.argv) >= 3:
        install(sys.argv[2], sync=("--no-sync" not in sys.argv[3:]))
    elif cmd == "restore":
        restore()
    else:
        print(__doc__)
