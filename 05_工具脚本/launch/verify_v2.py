# -*- coding: utf-8 -*-
"""
验证 D:\\BH3\\7.0\\server-v2\\run\\Server.exe 这套（.NET 8 + SQLite）确实起来了。

用法（先 launch_v2.py start，再跑本脚本，最后 launch_v2.py stop）：
  tools\\python\\python.exe _launch\\verify_v2.py

12 项：
  1  443 有监听且 exe == server-v2\\run\\Server.exe
  2  443 进程不是 PemukulPaku.exe（v1 已于 2026-10-25 移除，防串）
  3  27017 未监听（mongod 不参与）
  4  TCP 16100 可连
  5  HTTP 8081 /query_dispatch 200
  6  HTTPS 443 /query_dispatch 200
  7  v2 日志：Boot 行 + Handler 132（去重）
  8  v2 日志无异常
  9  SQLite 存在 / journal_mode=wal / 表清单
 10  query_gateway 返回 gameserver 与 16100
 11  nginx 大包 content-length 对得上磁盘
 12  登录链路：mdk login retcode=0 且 Users 表有行
"""

import ctypes
import json
import os
import socket
import sqlite3
import ssl
import subprocess
import sys
from ctypes import wintypes

ROOT = r"D:\BH3\7.0"
RUN = os.path.join(ROOT, r"server-v2\run")
EXPECT_EXE = os.path.join(RUN, "Server.exe")
V1_EXE_NAME = "PemukulPaku.exe"  # v1 已删除（2026-10-25），此处只按进程名防串
DB_FILE = os.path.join(RUN, r"data\pemukul.sqlite")
LOG = os.path.join(ROOT, r"_launch\logs\v2_Server.log")

# Global.Table<T>() 里声明的 12 张表；表是懒建的，没被访问过的不会出现在 sqlite_master
DECLARED = {"Users", "Avatars", "Equipments", "OpenWorlds", "Elfs", "Dorms",
            "ClientDatas", "Logins", "PrivateMessages", "DLCs", "GrandKeys",
            "AutoIncrements"}

ok = fail = 0


def ck(name, cond, extra=""):
    global ok, fail
    if cond:
        ok += 1
        print("  [ OK ] %-42s %s" % (name, extra))
    else:
        fail += 1
        print("  [FAIL] %-42s %s" % (name, extra))


def pid_on_port(port):
    r = subprocess.run(["netstat", "-ano", "-p", "TCP"], capture_output=True, timeout=10)
    txt = r.stdout.decode("utf-8", "replace") + r.stdout.decode("cp936", "replace")
    for line in txt.splitlines():
        p = line.split()
        if len(p) >= 5 and p[0].upper() == "TCP" and p[3].upper() == "LISTENING":
            if p[1].rsplit(":", 1)[-1] == str(port):
                try:
                    return int(p[4])
                except ValueError:
                    pass
    return None


def exe_of(pid):
    if not pid:
        return None
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    h = k32.OpenProcess(0x1000, False, int(pid))
    if not h:
        return None
    try:
        n = wintypes.DWORD(1024)
        buf = ctypes.create_unicode_buffer(n.value)
        if k32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(n)):
            return buf.value
    finally:
        k32.CloseHandle(h)
    return None


def raw_http(port, method, path, body=b"", headers=None, tls=False):
    s = socket.create_connection(("127.0.0.1", port), 6)
    if tls:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        s = ctx.wrap_socket(s, server_hostname="127.0.0.1")
    hd = {"Host": "127.0.0.1", "Connection": "close"}
    if body:
        hd["Content-Length"] = str(len(body))
        hd["Content-Type"] = "application/json"
    if headers:
        hd.update(headers)
    req = "%s %s HTTP/1.1\r\n" % (method, path)
    req += "".join("%s: %s\r\n" % kv for kv in hd.items()) + "\r\n"
    s.sendall(req.encode() + body)
    buf = b""
    while True:
        try:
            d = s.recv(65536)
        except socket.timeout:
            break
        if not d:
            break
        buf += d
        if len(buf) > 4 * 1024 * 1024:
            break
    s.close()
    head, _, payload = buf.partition(b"\r\n\r\n")
    lines = head.decode("latin1", "replace").split("\r\n")
    status = lines[0] if lines else ""
    hdrs = {}
    for ln in lines[1:]:
        if ":" in ln:
            k, v = ln.split(":", 1)
            hdrs[k.strip().lower()] = v.strip()
    if hdrs.get("transfer-encoding", "").lower() == "chunked":
        out, rest = b"", payload
        while True:
            i = rest.find(b"\r\n")
            if i < 0:
                break
            n = int(rest[:i].split(b";")[0] or b"0", 16)
            if n == 0:
                break
            out += rest[i + 2:i + 2 + n]
            rest = rest[i + 2 + n + 2:]
        payload = out
    return status, hdrs, payload


def as_json(payload):
    try:
        return json.loads(payload.decode("utf-8", "replace"))
    except Exception:
        return None


def read_host():
    try:
        with open(os.path.join(RUN, "config.json"), encoding="utf-8-sig") as f:
            return json.load(f).get("Gameserver", {}).get("Host", "?")
    except Exception:
        return "?"


# 用哪个账号试登录：默认新建一个专用测试号；导入过 v1 存档的话可以用已有账号
# （--account=test）验证「存档确实被读到了」而不是又建了一个新号
ACCOUNT = "v2verify"
for a in sys.argv[1:]:
    if a.startswith("--account="):
        ACCOUNT = a.split("=", 1)[1]


print("=" * 84)
print("验证 v2：server-v2\\run\\Server.exe（.NET 8 + SQLite）")
print("=" * 84)

# ---------------------------------------------------------------- 1 / 2
print("\n[1] 443 端口上的进程是谁")
pid = pid_on_port(443)
exe = exe_of(pid)
PID443 = pid  # 后面 [10] 用来确认「还是同一个进程、没有崩」
ck("443 有监听", pid is not None, "PID %s" % pid)
ck("exe == server-v2\\run\\Server.exe",
   bool(exe) and os.path.normcase(exe) == os.path.normcase(EXPECT_EXE), exe or "(取不到)")
ck("443 进程不是 PemukulPaku.exe",
   bool(exe) and os.path.basename(exe).lower() != V1_EXE_NAME.lower(), exe or "")

# ---------------------------------------------------------------- 3
print("\n[2] mongod 是否被牵连")
p27017 = pid_on_port(27017)
ck("27017 未监听（v2 不需要 mongod）", p27017 is None, "PID %s" % p27017)

# ---------------------------------------------------------------- 4
print("\n[3] TCP 16100")
s = socket.socket()
s.settimeout(2)
r = s.connect_ex(("127.0.0.1", 16100))
s.close()
ck("16100 可连", r == 0, "connect_ex=%d" % r)

# ---------------------------------------------------------------- 5 / 6
print("\n[4] HTTP 入口")
try:
    st, hd, pl = raw_http(8081, "GET", "/query_dispatch?version=7.0.0_os_pc")
    j = as_json(pl)
    ck("8081 /query_dispatch 200", st.split()[1] == "200", st)
    ck("retcode == 0", bool(j) and j.get("retcode") == 0,
       "retcode=%s" % (j or {}).get("retcode"))
    # 客户端会直接去连 dispatch_url，不带端口就会打到 80 的 nginx（404）→ 游戏报「连接失败」
    du = ((j or {}).get("region_list") or [{}])[0].get("dispatch_url") or ""
    ck("dispatch_url 带 HTTP 端口", (":8081/" in du), du or "(空)")
except Exception as e:
    ck("8081 /query_dispatch", False, repr(e))
try:
    st, hd, pl = raw_http(443, "GET", "/query_dispatch", tls=True)
    j = as_json(pl)
    ck("443 /query_dispatch 200 (TLS)", st.split()[1] == "200", st)
    ck("443 retcode == 0", bool(j) and j.get("retcode") == 0,
       "retcode=%s" % (j or {}).get("retcode"))
except Exception as e:
    ck("443 /query_dispatch", False, repr(e))

# ex_audio_and_video_url_list 的条目**不能带 scheme**：
# 客户端（WwiseAudioManager.CheckPackageManifestCoroutine）会无条件前置 "https://"，
# 返回 "http://..." 会被拼成 "https://http://..." → 主机名 "http" → 502。
try:
    st, hd, pl = raw_http(8081, "GET", "/query_gateway?version=7.0.0_os_pc")
    j = as_json(pl)
    ex = ((j or {}).get("ex_audio_and_video_url_list") or [""])[0]
    ck("ex_audio 不带 scheme", "://" not in ex, ex or "(空)")
    ck("ex_audio 指向本机", ("192.168" in ex or "127.0.0.1" in ex), ex or "(空)")
except Exception as e:
    ck("ex_audio_and_video_url_list", False, repr(e))

# 443 上的静态资源转发：客户端把 ex_audio 补成 https 后落在 Kestrel，
# 再由 StaticProxy 反代到 nginx:80 取**二进制清单**（不是目录索引！）。
# 返回 HTML 会让客户端 ParseManifest 抛 ArgumentException: length。
try:
    st, hd, pl = raw_http(443, "GET",
                          "/com.miHoYo.bh3oversea/Audio/Windows/7_0/0/", tls=True)
    ck("443 音频清单 200", st.split()[1] == "200", st)
    ck("443 音频清单不是 HTML", b"<html" not in pl.lower()[:200], "首字节 %r" % pl[:12])
    ck("443 音频清单大小 == 9234", len(pl) == 9234, "%d B" % len(pl))
    st, hd, pl = raw_http(443, "GET",
                          "/com.miHoYo.bh3oversea/StreamingAsb/7_0_0/pc/HD/asb/BlockMeta_7_0.xmf",
                          tls=True)
    ck("443 BlockMeta 200", st.split()[1] == "200", st)
    ck("443 BlockMeta 大小 == 14121", len(pl) == 14121, "%d B" % len(pl))
except Exception as e:
    ck("443 静态资源转发", False, repr(e))

# ---------------------------------------------------------------- 7 / 8
print("\n[5] v2 日志")
try:
    txt = open(LOG, encoding="utf-8", errors="replace").read()
    tail = txt[txt.rfind("Starting server v2"):] if "Starting server v2" in txt else txt
    types = set()
    for ln in tail.splitlines():
        if "Loaded PacketHandler" in ln and " for Packet Type " in ln:
            types.add(ln.split(" for Packet Type ", 1)[1].strip())
    ck("Boot 行 'Starting server v2'", "Starting server v2" in txt)
    ck("Handler 注册数 == 132（去重）", len(types) == 132, "%d 个" % len(types))
    bad = [l for l in tail.splitlines()
           if ("Exception" in l or "Unhandled" in l or "Could not load file or assembly" in l)]
    ck("本轮日志无异常", not bad, bad[0][:90] if bad else "干净")
except OSError as e:
    ck("读日志", False, repr(e))

# ---------------------------------------------------------------- 9
print("\n[6] SQLite")
try:
    ck("存档文件存在", os.path.exists(DB_FILE),
       "%.1f KB" % (os.path.getsize(DB_FILE) / 1024.0) if os.path.exists(DB_FILE) else DB_FILE)
    con = sqlite3.connect("file:%s?mode=ro" % DB_FILE.replace("\\", "/"), uri=True, timeout=5)
    try:
        jm = con.execute("PRAGMA journal_mode").fetchone()[0]
        ck("journal_mode == wal", str(jm).lower() == "wal", str(jm))
        tables = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        # 表是懒建的：Global.Table<T>() 第一次被调用时才 CREATE TABLE，
        # 所以这里只能要求「已建的表都在声明清单里」且登录用到的那两张已在
        ck("已建表都在 12 张声明清单内", set(tables) <= DECLARED,
           "%d 张：%s" % (len(tables), ",".join(tables)))
        ck("Users / AutoIncrements 已建", {"Users", "AutoIncrements"} <= set(tables),
           "缺 %s" % ({"Users", "AutoIncrements"} - set(tables)) if not {"Users", "AutoIncrements"} <= set(tables) else "")
    finally:
        con.close()
except Exception as e:
    ck("SQLite 读取", False, repr(e))

# ---------------------------------------------------------------- 10
print("\n[7] query_gateway")
try:
    st, hd, pl = raw_http(8081, "GET", "/query_gateway?version=7.0.0_os")
    j = as_json(pl) or {}
    # 这个接口是扁平的：{"retcode":0,"gameserver":{...},"gateway":{...},...}
    gs = j.get("gameserver") or (j.get("data") or {}).get("gameserver") or {}
    ck("返回 gameserver", bool(gs), str(gs)[:70])
    ck("port == 16100", str(gs.get("port")) == "16100", str(gs.get("port")))
    ck("ip == config.Host", gs.get("ip") == read_host(), "%s" % gs.get("ip"))
except Exception as e:
    ck("query_gateway", False, repr(e))

# ---------------------------------------------------------------- 11
print("\n[8] 静态资源（nginx :80）")
try:
    base = os.path.join(ROOT, r"runtime\web")
    cand = None
    for r_, d_, fs in os.walk(os.path.join(base, "asset_bundle")):
        for f in fs:
            p = os.path.join(r_, f)
            if os.path.getsize(p) > 2 * 1024 * 1024:
                cand = p
                break
        if cand:
            break
    rel = "/" + os.path.relpath(cand, base).replace("\\", "/")
    disk = os.path.getsize(cand)
    st, hd, _ = raw_http(80, "GET", rel)
    ck("大包 200", st.split()[1] in ("200", "206"), "%s  %d B" % (st, disk))
    ck("content-length 对得上", int(hd.get("content-length", -1)) == disk,
       "%s vs %d" % (hd.get("content-length"), disk))
except Exception as e:
    ck("静态资源", False, repr(e))

# ---------------------------------------------------------------- 12
print("\n[9] 登录链路（写库）")
try:
    body = json.dumps({"account": ACCOUNT, "password": "123456",
                       "is_crypto": False, "game_biz": "bh3_global"}).encode()
    st, hd, pl = raw_http(8081, "POST", "/hk4e_global/mdk/shield/api/login", body)
    j = as_json(pl) or {}
    acc = (j.get("data") or {}).get("account") or {}
    ck("mdk login 200", st.split()[1] == "200", st)
    ck("retcode == 0", j.get("retcode") == 0, "retcode=%s" % j.get("retcode"))
    ck("下发 uid / token", bool(acc.get("uid")) and bool(acc.get("token")),
       "uid=%s" % acc.get("uid"))
    con = sqlite3.connect("file:%s?mode=ro" % DB_FILE.replace("\\", "/"), uri=True, timeout=5)
    try:
        n = con.execute("SELECT COUNT(*) FROM Users").fetchone()[0]
        ck("Users 表有行", n >= 1, "%d 行" % n)
    finally:
        con.close()
except Exception as e:
    ck("登录链路", False, repr(e))

# ---------------------------------------------------------------- 13
# v1(Mongo) 的 C# 驱动会把属性 Id 映射成元素名 "_id"，
# 所以存档里武器/圣痕/材料/宿舍家具的物品 ID 都叫 "_id"。
# v2 换成 JSON 后如果不翻译，Id 会变成 0 —— 客户端拿不到物品 ID，
# 表现就是「能登录，但背包里武器/圣痕/材料显示不出来」。
print("\n[10] 装备物品 ID（_id -> Id 翻译）")
try:
    con = sqlite3.connect("file:%s?mode=ro" % DB_FILE.replace("\\", "/"), uri=True, timeout=5)
    try:
        rows = con.execute("SELECT owner_uid, payload FROM Equipments;").fetchall()
        resid = sum((p or "").count('"_id"') for _, p in rows)
        ck("没有残留的 _id 键", resid == 0, "%d 处" % resid)

        zero = []
        total = 0
        for uid, payload in rows:
            j = json.loads(payload or "{}")
            for key in ("WeaponList", "StigmataList", "MaterialList", "MechaList"):
                for it in (j.get(key) or []):
                    total += 1
                    if not it.get("Id"):
                        zero.append("%s/uid%s" % (key, uid))
        ck("每件装备/材料都有 Id", not zero,
           "%d 件，缺失 %d%s" % (total, len(zero), ("（" + zero[0] + "）") if zero else ""))

        rich = [(u, len(json.loads(p or "{}").get("WeaponList") or []),
                 len(json.loads(p or "{}").get("StigmataList") or [])) for u, p in rows]
        best = max(rich, key=lambda x: x[1] + x[2]) if rich else (None, 0, 0)
        ck("至少一个账号有装备", best[1] + best[2] > 0,
           "uid=%s 武器 %d / 圣痕 %d" % best)
    finally:
        con.close()
except Exception as e:
    ck("装备物品 ID", False, repr(e))

# ---------------------------------------------------------------- 14
# 回归防护：前面 [3] 对 16100 做过一次「连上就断」的探活。
# 旧版 Session.DisconnectProtocol() 在 Player == null 时直接 Player.SaveAll()，
# 抛 NullReferenceException 的是后台线程 → 整个 Server.exe 凭空消失。
# 表现是：verify 跑到一半还好好的，后面的检查全部 ConnectionRefused。
print("\n[11] 探活之后服务端是否还活着（防 Session 空引用崩进程）")
pid = pid_on_port(443)
ck("443 仍有监听", pid is not None, "PID %s" % pid)
ck("还是同一个进程", pid == PID443, "start=%s now=%s" % (PID443, pid))
ck("进程仍在运行", bool(exe_of(pid)), exe_of(pid) or "(已退出)")

print("\n" + "=" * 84)
print("结果：%d 通过 / %d 失败" % (ok, fail))
print("=" * 84)
sys.exit(1 if fail else 0)
