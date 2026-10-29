"""检测 metadata 高熵区是否为短密钥 XOR 加密"""
from collections import Counter
import sys

p = r'BH3_Data/Managed/Metadata/global-metadata.dat'
data = open(p, 'rb').read()

REGIONS = [
    ('头后大块A',   0x51000, 0x564000),
    ('明文带1前',   0xAC0000, 0xEC0000),
    ('中段大块B',   0xFA0000, 0x1C30000),
    ('字面量带后',  0x1EC0000, 0x2420000),
    ('后段大块C',   0x24B0000, 0x3160000),
]

def byte_hist(b):
    c = Counter(b)
    return c

def try_single_xor(b):
    """对每个单字节 key，统计解密后可打印比例"""
    best = []
    n = len(b)
    for k in range(256):
        printable = sum(1 for x in b[:65536] if 32 <= (x ^ k) < 127 or (x ^ k) == 0)
        best.append((printable / 65536, k))
    best.sort(reverse=True)
    return best[:3]

def keylen_autocorr(b, maxlen=33):
    """自相关法测 XOR 密钥长度：
    若 key 长度 K，则 plain[i]^plain[i+K] = data[i]^data[i+K]（key 相消）。
    对 ASCII 文本，两字母 XOR 通常 < 0x20；错位时则是随机字节 XOR，>=0x80 概率高。
    这里统计 data[i]^data[i+K] 中 < 0x20 的占比，找异常峰。"""
    res = []
    n = len(b)
    for K in range(1, maxlen):
        cnt = 0
        total = 0
        for i in range(0, min(n, 200000) - K):
            x = b[i] ^ b[i + K]
            total += 1
            if x < 0x20:
                cnt += 1
        res.append((cnt / total, K))
    res.sort(reverse=True)
    return res[:5]

for name, s, e in REGIONS:
    b = data[s:e]
    c = byte_hist(b[:2**20])
    top = c.most_common(4)
    print(f'== {name} [{s:#x}..{e:#x}] {len(b)/1048576:.1f}MB')
    print(f'   top字节: {[("%02x(%d)"%(k,v)) for k,v in top]}')
    sr = try_single_xor(b)
    print(f'   单字节XOR最优: {[(f"{r:.2f}",hex(k)) for r,k in sr]}')
    ak = keylen_autocorr(b)
    print(f'   自相关峰: {[(f"{r:.3f}",K) for r,K in ak]}')
