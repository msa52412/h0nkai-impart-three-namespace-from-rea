# -*- coding: utf-8 -*-
import sys, struct
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4block import lz4_block_decompress

raw = open(r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc/f65865df27ea6a9e58bf8f1f3b01bdcd.wmv.orig","rb").read()
n = len(raw)
print("文件 %d 字节" % n)

found = []
for cand in range(60, n - 24):
    probe = lz4_block_decompress(raw[cand:cand + 40])
    if len(probe) < 20: continue
    ms, fs, ver, do = struct.unpack_from(">IIII", probe, 0)
    if not (0 < ms < (1 << 20) and 0 < fs < (1 << 26) and ver == 17): continue
    if do < ms or do > fs: continue
    full = lz4_block_decompress(raw[cand:], stop_at=fs)
    if len(full) != fs: continue
    found.append((cand, ms, fs, do, len(full)))

print("有效 LZ4/SerializedFile 起点 %d 个:" % len(found))
for f in found:
    print("  bodyOff=%-6d meta=%-6d file=%-7d dataOff=%-6d 解压=%-7d" % f)

# 在解压体里找类型名
for off, ms, fs, do, _ in found:
    body = lz4_block_decompress(raw[off:], stop_at=fs)
    hits = [k for k in (b"Texture2D", b"m_Width", b"m_Name", b"m_TextureFormat", b"add.png", b"backicon") if k in body]
    print("  @%-6d 关键字: %s" % (off, [h.decode() for h in hits]))
