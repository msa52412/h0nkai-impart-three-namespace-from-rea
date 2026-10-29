# -*- coding: utf-8 -*-
"""pkg_version 清单同步工具

背景
----
D:\\BH3\\7.0\\pkg_version 是启动器的文件完整性清单，186 行 JSONL，
每行一个文件：{"remoteName": "...", "md5": "大写32位", "fileSize": N}

覆盖范围 = BH3.exe + UnityPlayer.dll + BH3_Data/ 下 184 个文件
（含 BH3_Data/Native/UserAssembly.dll），**不含 StreamingAssets/*.wmv**，
所以改 wmv 从来不触发校验，改这几个核心文件就会报「游戏文件缺失 X」。

改完文件后把对应行的 md5 / fileSize 同步即可通过校验。

用法
----
    python pkg_fix.py check                  核对全部条目
    python pkg_fix.py update <相对路径>      重算并写回单条
    python pkg_fix.py update-all             重算全部已存在文件
    python pkg_fix.py restore                还原清单备份
"""
import sys, os, json, hashlib, shutil, re

ROOT = r"D:\BH3\7.0"
PKG = os.path.join(ROOT, "pkg_version")
BAK = PKG + ".bak_pkg"


def read_lines():
    with open(PKG, "rb") as f:
        raw = f.read()
    return raw


def load():
    rows = []
    for ln in read_lines().split(b"\n"):
        if not ln.strip():
            continue
        rows.append(json.loads(ln.decode("utf-8")))
    return rows


def dump(rows):
    out = []
    for r in rows:
        out.append(json.dumps({"remoteName": r["remoteName"],
                               "md5": r["md5"],
                               "fileSize": r["fileSize"]},
                              ensure_ascii=False))
    return ("\n".join(out) + "\n").encode("utf-8")


def md5_of(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        while True:
            b = f.read(1 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest().upper()


def check():
    rows = load()
    bad, missing = [], []
    for r in rows:
        p = os.path.join(ROOT, r["remoteName"].replace("/", os.sep))
        if not os.path.exists(p):
            missing.append(r["remoteName"]); continue
        sz = os.path.getsize(p)
        if sz != r["fileSize"]:
            bad.append((r["remoteName"], "大小 %d != 清单 %d" % (sz, r["fileSize"]))); continue
    print("条目 %d，缺失 %d，大小不符 %d" % (len(rows), len(missing), len(bad)))
    for m in missing[:10]:
        print("  缺失:", m)
    for n, why in bad[:10]:
        print("  不符: %-50s %s" % (n, why))
    return not missing and not bad


def update_one_inplace(rel):
    """原地替换该行的 32 位 md5 十六进制（保持文件其余字节完全不变）。

    原 pkg_version 的行格式并不统一：绝大多数是
        {"remoteName": "X", "md5": "Y", "fileSize": N}
    但 global-metadata.dat 那行是紧凑格式
        {"remoteName":"X","md5":"Y","fileSize":N}
    说明它是被启动器自己重写过的。整个文件只有 22 KB，重排格式会改变
    字节长度，风险不必要 —— 因此这里只在原位置覆写 md5 字符串。
    """
    rel = rel.replace("\\", "/")
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    if not os.path.exists(p):
        print("文件不存在:", p); return False
    new_md5 = md5_of(p)
    new_sz = os.path.getsize(p)

    raw = read_lines()
    needle = ('"remoteName": "%s"' % rel).encode()
    i = raw.find(needle)
    if i < 0:
        # 紧凑格式
        needle2 = ('"remoteName":"%s"' % rel).encode()
        i = raw.find(needle2)
        if i < 0:
            print("清单中没有这条:", rel); return False

    # 在该行内定位 md5
    line_start = raw.rfind(b"\n", 0, i) + 1
    line_end = raw.find(b"\n", i)
    if line_end < 0:
        line_end = len(raw)
    line = raw[line_start:line_end]
    # 用正则精确定位 md5 值的 32 位十六进制
    m = re.search(rb'"md5"\s*:\s*"([0-9A-Fa-f]{32})"', line)
    if not m:
        print("该行没有可识别的 md5 字段"); return False
    mstart = line_start + m.start(1)
    mend = line_start + m.end(1)
    old = raw[mstart:mend].decode()
    if old == new_md5:
        print("%-46s md5 已一致，无需改动" % rel); return True

    out = bytearray(raw)
    out[mstart:mend] = new_md5.encode().ljust(32, b"0")[:32]

    mfs = re.search(rb'"fileSize"\s*:\s*(\d+)', line)
    if mfs:
        fs_start = line_start + mfs.start(1)
        fs_end = line_start + mfs.end(1)
        old_sz = raw[fs_start:fs_end].decode()
        if old_sz != str(new_sz):
            new_s = str(new_sz).encode()
            if len(new_s) == len(old_sz):
                out[fs_start:fs_end] = new_s
                print("  文件大小 %s -> %d" % (old_sz, new_sz))
            else:
                print("  ! 文件大小位数变化（%s -> %d），无法原地替换，请用 update-all"
                      % (old_sz, new_sz))
                return False

    if not os.path.exists(BAK):
        shutil.copy2(PKG, BAK)
        print("[+] 已备份 ->", BAK)
    with open(PKG, "wb") as f:
        f.write(bytes(out))
    print("%-46s %s -> %s  (原地，长度不变 %d)" % (rel, old[:16], new_md5[:16], len(out)))
    return True


def update_one(rel, rows=None, save=True):
    """保留旧接口：默认走原地替换，不做重排。"""
    return update_one_inplace(rel)


def update_all():
    rows = load()
    n = 0
    for r in rows:
        p = os.path.join(ROOT, r["remoteName"].replace("/", os.sep))
        if not os.path.exists(p):
            continue
        cur = md5_of(p)
        if cur != r["md5"] or os.path.getsize(p) != r["fileSize"]:
            r["md5"] = cur
            r["fileSize"] = os.path.getsize(p)
            print("  更新:", r["remoteName"])
            n += 1
    if n == 0:
        print("全部一致，无需更新"); return
    if not os.path.exists(BAK):
        shutil.copy2(PKG, BAK)
        print("[+] 已备份 ->", BAK)
    with open(PKG, "wb") as f:
        f.write(dump(rows))
    print("[+] 共更新 %d 条" % n)


def restore():
    if not os.path.exists(BAK):
        print("没有备份"); return
    shutil.copy2(BAK, PKG)
    print("[+] 已还原清单", BAK)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "check":
        check()
    elif cmd == "update":
        for a in sys.argv[2:]:
            update_one(a)
    elif cmd == "update-all":
        update_all()
    elif cmd == "restore":
        restore()
    else:
        print(__doc__)
