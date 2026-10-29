# -*- coding: utf-8 -*-
"""T7 (0x10/条) + T8 (0x2C/条) = assembly 定义表全解
   T7 @ E60^0x371B8070, T8 @ E70^0x0561C6FD
   uVar23 = ((i*0x56184A41 + 0x57A94B1F) ^ 0x37F164B8) * 0x10FB44E5 ^ 0x7B1DE297
   uVar25 = (i*0x447FCE41 ^ 0x120DD35F) * 0x3E8906DA"""
import struct
import sys

sys.path.insert(0, r"D:\Carol-start\_rea")
from probe_thunk import PE

pe = PE(r"D:\Carol-start\_rea\UserAssembly_slim.dll")
BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
M32 = 0xFFFFFFFF
M64 = (1 << 64) - 1
BASE = 0x118

raw_e60 = struct.unpack_from("<I", pe.d, pe.va2off(0x188198E60))[0]
raw_e70 = struct.unpack_from("<I", pe.d, pe.va2off(0x188198E70))[0]
T7 = BASE + (raw_e60 ^ 0x371B8070)
T8 = BASE + (raw_e70 ^ 0x0561C6FD)
print("T7 @0x%X, T8 @0x%X" % (T7, T8))


def k7(i):
    v = (i * 0x56184A41 + 0x57A94B1F) & M32
    v ^= 0x37F164B8
    v = (v * 0x10FB44E5) & M32
    return v ^ 0x7B1DE297


def k8(i):
    v = (i * 0x447FCE41) & M32
    v ^= 0x120DD35F
    v = (v * 0x3E8906DA) & M32
    return v


K_MUL = (-0x394A88E12FFFF3A0) & M64
K_ADD = 0x53DB1FC7E9ECC644
K_STEP = 0x64C7CE0352814CF6
POOL = BASE + 0x24AAC18
def dstr(pid):
    L = (pid >> 24) & 0xFF
    if L == 0 or L > 0x60:
        return ""
    ix = pid & 0xFFFFFF
    key = (ix * K_MUL + K_ADD) & M64
    out = bytearray()
    for b in range((L + 7) >> 3):
        out += (struct.unpack_from("<Q", BUF, POOL + ix + b * 8)[0] ^ key).to_bytes(8, "little")
        key = (key + K_STEP) & M64
    return bytes(out[:L]).decode("utf-8", "replace")


N = 192
rows = []
for i in range(N):
    t7 = struct.unpack_from("<4I", BUF, T7 + i * 0x10)
    t8 = struct.unpack_from("<11I", BUF, T8 + i * 0x2C)
    a = k7(i)
    b = k8(i)
    rows.append({
        "imgIdx": ((t7[2] + 0xFC36A893) - a) & M32,
        "f0": ((t7[0] ^ 0x6E35EDFF) - a + 0x23E109DE) & M32,
        "f1": ((t7[1] ^ 0x242D7F7E) - a) & M32,
        "f3": ((t7[3] ^ 0x755539F1) - a + 0x76CB3B6D) & M32,
        "name": dstr((t8[1] + 0x84B0104A) & M32 ^ b),
        "culture": dstr(((t8[5] + 0xF54D97A6) & M32) ^ b),
        "pubkey": dstr(((t8[7] + 0xFECCC2CD) & M32) ^ b ^ 0x4FBC7CFF),
        "hash1": dstr(((t8[3] ^ 0x7B3F167F) ^ b ^ 0x6B612990)),
        "a8": ((t8[8] + 0xA48472E0) & M32) ^ b ^ 0x39FD8DCC,
        "a4": (t8[4] ^ 0x2B15FEC1) ^ b ^ 0x2779C1DD,
        "a2": (t8[2] ^ 0x38BB4148) ^ b ^ 0x448AE27E,
        "a0": (t8[0] ^ 0x348873DC) ^ b ^ 0x41E927B0,
        "a6": (((t8[6] + 0x8F726A05) & M32) ^ b + 0x28F01FF2) & M32,
    })

ok = sum(1 for r in rows if r["name"] and r["name"].endswith(".dll"))
print("assembly 名 .dll 结尾: %d / %d" % (ok, N))
for i in (0, 1, 2, 120, 191):
    r = rows[i]
    print("  [%3d] %-40s img=%-4d v%d.%d.%d.%d culture=%r" %
          (i, r["name"][:40], r["imgIdx"], r["a0"], r["a4"], r["a8"], r["a6"], r["culture"]))

with open(r"D:\Carol-start\_rea\bh3_assemblies.tsv", "w", encoding="utf-8", newline="\n") as f:
    f.write("asmIdx\tname\timageIdx\tver_a\tver_b\tver_c\tver_d\tculture\tpublicKey\n")
    for i, r in enumerate(rows):
        f.write("%d\t%s\t%d\t%d\t%d\t%d\t%d\t%s\t%s\n" %
                (i, r["name"], r["imgIdx"], r["a0"], r["a4"], r["a8"], r["a6"],
                 r["culture"], r["pubkey"]))
print("已写 bh3_assemblies.tsv")
