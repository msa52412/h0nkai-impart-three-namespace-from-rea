# -*- coding: utf-8 -*-
"""ctable.dat 密钥流工具。

原理
----
若 ctable 的最外层是流密码（或 CTR 模式），则
    密文[i] = 明文[i] XOR 密钥流[i]
密钥流与明文无关，因此只要有一份「同一版本、同一偏移」的明文/密文对，
就能算出整段密钥流，之后任意改写明文都能原地重加密，**不需要密钥**。

若最外层是 CBC，则 P[i] = D(C[i]) XOR C[i-1]，密钥流不可直接复用。

对齐问题
--------
内存 dump 出来的明文块，起点通常不等于 ctable.dat 的偏移 0（前面可能有
分配器头、vector 头、填充等）。流密码的密钥流是伪随机的，**没法用统计方法
反推对齐**，只能靠明文自身的结构特征定位。所以先用 `probe` 找容器头。

用法
----
    # 0) 看 dump 里有什么：找压缩/容器魔数，定位明文起点
    python ctable_crack.py probe <dump.bin> [--max 64]

    # 1) 用明文与 ctable.dat 对照，判定加密模式
    python ctable_crack.py check <dump.bin> [--pt-offset N] [--ct-offset N]

    # 2) 生成密钥流
    python ctable_crack.py keystream <dump.bin> [--pt-offset N] -o keystream.bin

    # 3) 用密钥流把改好的明文加密回去
    python ctable_crack.py encrypt <new_plain.bin> <keystream.bin> -o new_ctable.dat
"""
import sys, os, struct, collections, math

CTABLE = r"D:\BH3\7.0\BH3_Data\StreamingAssets\ctable.dat"

# 常见的容器 / 压缩魔数
MAGICS = [
    (b"\x1f\x8b\x08", "gzip"),
    (b"BZh", "bzip2"),
    (b"\x28\xb5\x2f\xfd", "zstd"),
    (b"\x04\x22\x4d\x18", "lz4-frame"),
    (b"UnityFS\x00", "UnityFS"),
    (b"UnityWeb", "UnityWeb"),
    (b"PK\x03\x04", "zip"),
    (b"SQLite format 3\x00", "sqlite"),
    (b"MHY\x00", "MHY-header"),
    (b"ExcelOutputAsset", "ExcelOutputAsset 明文"),
    (b"SpriteOutput/WorldMap", "WorldMap 贴图路径明文"),
    (b"[{", "JSON 数组开头"),
]
# zlib 头需要额外校验（0x78 后第二字节满足 %31==0）
def is_zlib(b):
    return len(b) >= 2 and b[0] == 0x78 and (b[0] * 256 + b[1]) % 31 == 0


def xor(a, b):
    n = min(len(a), len(b))
    return bytes(x ^ y for x, y in zip(a[:n], b[:n]))


def hexdump(b, n=64):
    b = b[:n]
    out = []
    for i in range(0, len(b), 16):
        chunk = b[i:i + 16]
        hx = " ".join("%02x" % c for c in chunk).ljust(47)
        tx = "".join(chr(c) if 32 <= c < 127 else "." for c in chunk)
        out.append("  %08x  %s  %s" % (i, hx, tx))
    return "\n".join(out)


def probe(path, max_hits=64):
    data = open(path, "rb").read()
    print("文件 %s, %d 字节" % (path, len(data)))
    print("\n--- 开头 128 字节 ---")
    print(hexdump(data, 128))

    print("\n--- 魔数命中 ---")
    found = []
    for magic, name in MAGICS:
        start = 0
        cnt = 0
        while cnt < 8:
            i = data.find(magic, start)
            if i < 0:
                break
            found.append((i, name, len(magic)))
            start = i + 1
            cnt += 1
    # zlib 单独扫（用 find 加速，避免逐字节 Python 循环）
    i = data.find(b"\x78")
    zc = 0
    while i >= 0 and zc < 24:
        if is_zlib(data[i:i + 2]):
            found.append((i, "zlib", 2))
            zc += 1
        i = data.find(b"\x78", i + 1)

    found.sort()
    if not found:
        print("  无命中。明文可能是自定义容器，或该区并非配置明文。")
    seen = set()
    shown = 0
    for off, name, ln in found:
        if shown >= max_hits:
            print("  ...(还有更多，已截断)")
            break
        key = (name, off >> 12)
        if key in seen:
            continue
        seen.add(key)
        shown += 1
        ctx = data[off:off + 48]
        print("  0x%08X  %-22s  %s" % (off, name,
              "".join(chr(c) if 32 <= c < 127 else "." for c in ctx)))

    # 熵
    n = min(len(data), 1 << 20)
    c = collections.Counter(data[:n])
    ent = -sum(v / n * math.log2(v / n) for v in c.values())
    print("\n前 %d 字节熵 = %.4f" % (n, ent))
    print("（8.0 附近=密文/已压缩；明显低于 8=有大量结构化文本）")


def check(plain_path, pt_off=0, ct_off=0):
    ct = open(CTABLE, "rb").read()
    pt_all = open(plain_path, "rb").read()
    pt = pt_all[pt_off:]
    print("ctable %d B, dump %d B (pt_off=%d), 对照起点 ct_off=%d"
          % (len(ct), len(pt_all), pt_off, ct_off))
    seg = ct[ct_off:ct_off + len(pt)]
    n = min(len(seg), len(pt))
    if n <= 0:
        print("!! 长度不匹配，无法对照")
        return None
    seg, pt = seg[:n], pt[:n]
    ks = xor(seg, pt)

    print("\n--- 密钥流前 32 字节 ---")
    print(" ", ks[:32].hex())
    print("\n--- 明文前 64 字节 ---")
    print(hexdump(pt, 64))

    # 一致性：CBC 下 P[i] = D(C[i]) ^ C[i-1]，所以 ks[i] = D(C[i]) 只依赖 C[i]；
    # 若同一 16 字节密文块出现两次，其 ks 也应完全相同 —— 流密码同样成立。
    # 真正的判据：CBC 的 ks 每块内部随机，但相邻块无关联；
    # 这里给一个更实用的信号：若 ks 在 16 字节边界上有明显重复周期，说明是重复密钥流。
    rep = 0
    for period in (16, 32, 64, 256):
        hits = 0
        for i in range(period, min(len(ks) - period, 65536), period):
            if ks[i:i + 16] == ks[i - period:i - period + 16]:
                hits += 1
        if hits > 64:
            print("\n[!] 密钥流在 %d 字节周期上大量重复 -> 固定密钥流，可直接复用" % period)
            rep = period
            break
    if not rep:
        print("\n密钥流无短周期重复（正常，CTR/流密码的典型表现）")

    nb = min(len(ks), 1 << 16)
    c = collections.Counter(ks[:nb])
    ent = -sum(v / nb * math.log2(v / nb) for v in c.values())
    print("密钥流前 %d 字节熵 = %.4f （≈8 即为合格伪随机流）" % (nb, ent))

    # 明文可打印比例：真正的明文应该大部分可读
    probe_n = min(len(pt), 4096)
    printable = sum(1 for b in pt[:probe_n] if 32 <= b < 127 or b in (9, 10, 13))
    print("明文前 %d 字节可打印比例 = %.3f" % (probe_n, printable / probe_n))
    if printable / probe_n < 0.5:
        print("   [!] 可打印比例偏低 —— 对齐点可能不对，先用 probe 找容器头再设 --pt-offset")

    print("\n判定：")
    print("  若上面明文前 64 字节是可读的结构化内容（JSON/魔数），")
    print("  则 ctable 的最外层为流密码/CTR，密钥流可复用，本工具链成立。")
    print("  若明文仍是乱码，说明 --pt-offset 没对齐，或最外层是 CBC（需另找密钥）。")
    return ks


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    cmd = sys.argv[1]

    def opt(name, default=None):
        if name in sys.argv:
            return sys.argv[sys.argv.index(name) + 1]
        return default

    if cmd == "probe":
        probe(sys.argv[2], int(opt("--max", 64)))
    elif cmd == "check":
        check(sys.argv[2], int(opt("--pt-offset", 0)), int(opt("--ct-offset", 0)))
    elif cmd == "keystream":
        out = opt("-o", "keystream.bin")
        ks = check(sys.argv[2], int(opt("--pt-offset", 0)), int(opt("--ct-offset", 0)))
        if ks:
            open(out, "wb").write(ks)
            print("[+] 写出 %s (%d B)" % (out, len(ks)))
    elif cmd == "encrypt":
        np_ = open(sys.argv[2], "rb").read()
        ks = open(sys.argv[3], "rb").read()
        if len(np_) > len(ks):
            print("!! 明文 %d B 超出密钥流覆盖 %d B" % (len(np_), len(ks)))
            return
        out = opt("-o", "new_ctable.dat")
        open(out, "wb").write(xor(np_, ks))
        print("[+] 写出 %s (%d B)" % (out, len(np_)))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
