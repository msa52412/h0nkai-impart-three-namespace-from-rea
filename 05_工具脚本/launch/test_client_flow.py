# -*- coding: utf-8 -*-
"""
模拟游戏客户端的「登录前握手」，全程走系统代理（mitmdump:8891），用来验证
「启动游戏报连接失败」这类问题到底断在哪一环。

客户端实际顺序（从 mitm 日志还原）：
  1. CONNECT global01.os.honkaiimpact3.com:443   -> mitm 按 SNI 改到 127.0.0.1:443
     GET /query_dispatch?version=7.0.0_os_pc     -> 拿 region_list[0].dispatch_url
  2. GET <dispatch_url>?version=7.0.0_os_pc      -> 拿 gameserver{ip,port} / account_url
  3. 连 gameserver 的 16100（这一步是游戏内协议，脚本不测）

用法（服务端已启动）：
  tools\\python\\python.exe _launch\\test_client_flow.py [--proxy 127.0.0.1:8891]
"""

import json
import socket
import ssl
import sys

PROXY = ("127.0.0.1", 8891)
for a in sys.argv[1:]:
    if a.startswith("--proxy="):
        h, p = a.split("=", 1)[1].rsplit(":", 1)
        PROXY = (h, int(p))

DISPATCH_HOST = "global01.os.honkaiimpact3.com"
VERSION = "7.0.0_os_pc"

ok = fail = 0


def ck(name, cond, extra=""):
    global ok, fail
    if cond:
        ok += 1
        print("  [ OK ] %-40s %s" % (name, extra))
    else:
        fail += 1
        print("  [FAIL] %-40s %s" % (name, extra))


def dechunk(body):
    out, rest = b"", body
    while True:
        i = rest.find(b"\r\n")
        if i < 0:
            return out
        try:
            n = int(rest[:i].split(b";")[0] or b"0", 16)
        except ValueError:
            return out
        if n == 0:
            return out
        out += rest[i + 2:i + 2 + n]
        rest = rest[i + 2 + n + 2:]


def read_all(s):
    buf = b""
    while True:
        try:
            d = s.recv(65536)
        except (socket.timeout, ssl.SSLError):
            break
        if not d:
            break
        buf += d
    head, _, body = buf.partition(b"\r\n\r\n")
    low = head.lower()
    if b"transfer-encoding: chunked" in low:
        body = dechunk(body)
    elif b"content-length" in low:
        try:
            n = int([l.split(b":", 1)[1] for l in head.split(b"\r\n")
                     if l.lower().startswith(b"content-length")][0])
            body = body[:n]
        except Exception:
            pass
    return head, body


def https_via_proxy(host, path):
    """走代理 CONNECT 隧道 + 不校验证书（mitm 用的是自签/上游证书）"""
    s = socket.create_connection(PROXY, 8)
    s.sendall(("CONNECT %s:443 HTTP/1.1\r\nHost: %s:443\r\n\r\n" % (host, host)).encode())
    head, _ = read_all(s)
    if b" 200" not in head.split(b"\r\n")[0]:
        return None, head[:120], b""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ss = ctx.wrap_socket(s, server_hostname=host)
    ss.sendall(("GET %s HTTP/1.1\r\nHost: %s\r\nUser-Agent: bh3/7.0.0\r\n"
                "Accept: */*\r\nConnection: close\r\n\r\n" % (path, host)).encode())
    head, body = read_all(ss)
    ss.close()
    return head.split(b"\r\n")[0], head, body


def http_via_proxy(url):
    """绝对 URI 形式的明文请求，和客户端拿到 dispatch_url 后做的事一样"""
    host_path = url.split("://", 1)[1]
    host = host_path.split("/", 1)[0]
    s = socket.create_connection(PROXY, 8)
    s.sendall(("GET %s HTTP/1.1\r\nHost: %s\r\nUser-Agent: bh3/7.0.0\r\n"
               "Accept: */*\r\nConnection: close\r\n\r\n" % (url, host)).encode())
    head, body = read_all(s)
    s.close()
    return head.split(b"\r\n")[0], head, body


print("=" * 84)
print("模拟客户端握手（经代理 %s:%d）" % PROXY)
print("=" * 84)

print("\n[1] query_dispatch（https，SNI=%s）" % DISPATCH_HOST)
st, head, body = https_via_proxy(DISPATCH_HOST, "/query_dispatch?version=%s&t=%d" % (VERSION, 1))
ck("状态 200", bool(st) and b" 200" in st, (st or b"?").decode("latin1"))
url = None
try:
    j = json.loads(body.decode("utf-8", "replace"))
    url = j["region_list"][0]["dispatch_url"]
    ck("retcode == 0", j.get("retcode") == 0, "retcode=%s" % j.get("retcode"))
    ck("dispatch_url 带端口", ":" in url.split("//", 1)[1], url)
except Exception as e:
    ck("解析 dispatch_url", False, repr(e)[:80] + " / " + body[:120].decode("latin1", "replace"))

print("\n[2] 请求 dispatch_url（明文，客户端就是这么连的）")
bundle = []
if url:
    st, head, body = http_via_proxy("%s?version=%s" % (url, VERSION))
    ck("状态 200", bool(st) and b" 200" in st, (st or b"?").decode("latin1"))
    try:
        j = json.loads(body.decode("utf-8", "replace"))
        gs = j.get("gameserver") or {}
        ck("gameserver 有 ip/port", bool(gs.get("ip")) and bool(gs.get("port")),
           "%s:%s" % (gs.get("ip"), gs.get("port")))
        ck("account_url 带端口", ":" in (j.get("account_url") or "").split("//", 1)[-1],
           j.get("account_url"))
        bundle = j.get("asset_bundle_url_list") or []
    except Exception as e:
        ck("解析 query_gateway", False, repr(e)[:80])

print("\n[3] 资源包地址（数值文件就在这里面）")
if bundle:
    b0 = bundle[0]
    ck("指向本地而不是 CDN", "akamaized.net" not in b0 and "honkaiimpact3.com" not in b0, b0)
    ck("带 /asset_bundle 前缀", "/asset_bundle/" in b0, b0)
    # 客户端拿到地址后，第一件事就是拉三个 build.status
    for sub in ("data/build.status", "event/build.status", "ai/build.status"):
        st, head, body = http_via_proxy("%s/%s" % (b0.rstrip("/"), sub))
        code = (st or b"?").decode("latin1")
        ck("%-22s 200" % sub, b" 200" in (st or b""), code + "  " + body[:24].decode("latin1", "replace"))
else:
    ck("asset_bundle_url_list", False, "空")

print("\n[4] 音视频/流式资源清单（客户端 CheckStreamingAssetBundle 会查这两个）")
try:
    st, head, body = http_via_proxy("%s?version=%s" % (url, VERSION))
    j = json.loads(body.decode("utf-8", "replace"))
    ex = (j.get("ex_audio_and_video_url_list") or [""])[0]

    # ★ 这个字段客户端会**无条件**前置 "https://"（不判断有没有 scheme）。
    #   曾经返回过 "http://192.168.0.103/..."，被拼成
    #   "https://http://192.168.0.103/..." → 主机名 "http" → 502 →
    #   客户端报「下载活动资源失败」。所以这里必须断言没有 "://"。
    ck("不带 scheme（host+path）", "://" not in ex, ex)
    ck("指向本机", "192.168" in ex or "127.0.0.1" in ex, ex)

    # 客户端实际请求的是 https://<ex>/<sub>，落在 443（Kestrel），
    # 由 StaticProxy 反代到 nginx:80 —— 这条链必须整条通。
    ex_host, _, ex_path = ex.partition("/")
    ex_path = "/" + ex_path

    # ★ 这两个是**二进制清单**，不是目录索引页。
    #   返回 HTML 会让客户端 WwiseAudioManager.ParseManifest 抛
    #   System.ArgumentException: length，重试 3 次后照样「下载活动资源失败」。
    #   期望大小 = 本地文件大小：manifest.m 9,234 B、BlockMeta.xmf 14,121 B
    #   （v1 成功那次 mitm 日志记的是 9.0k / 13.8k，正好对上）。
    cases = (
        ("Audio/Windows/7_0/0/", 9234),
        ("StreamingAsb/7_0_0/pc/HD/asb/BlockMeta_7_0.xmf", 14121),
    )
    for sub, want_len in cases:
        st, head, body = https_via_proxy(ex_host, "%s/%s" % (ex_path.rstrip("/"), sub))
        code = (st or b"?").decode("latin1")
        ck("%-42s 200" % sub, bool(st) and b" 200" in st, "%s  %d B" % (code, len(body)))
        ck("%-42s 不是 HTML" % sub, b"<html" not in body.lower()[:200],
           "首字节 %r" % body[:12])
        ck("%-42s 大小 == %d" % (sub, want_len), len(body) == want_len,
           "实际 %d B" % len(body))
except Exception as e:
    ck("ex_audio_and_video_url_list", False, repr(e)[:80])

print("\n[5] 反面验证：80 端口上没有 query_gateway（旧写法会 404）")
st, head, body = http_via_proxy("http://192.168.0.103/query_gateway?version=%s" % VERSION)
ck("80 端口 404（符合预期）", bool(st) and b" 404" in st, (st or b"?").decode("latin1"))
print("\n" + "=" * 84)
print("结果：%d 通过 / %d 失败" % (ok, fail))
print("=" * 84)
sys.exit(1 if fail else 0)
