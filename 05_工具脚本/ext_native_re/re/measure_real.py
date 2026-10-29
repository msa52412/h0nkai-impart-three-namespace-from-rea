"""真实数据实测：在 bundle payload 上改字节，看结构保持重放的等长成功率。

测三类典型改动（都是真实任务需要的）：
  A. 改字符串（等长），例如 Task_3 -> Task_4
  B. 改 pathID（8 字节 i64）
  C. 改连续一小段无关字节
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmvkit as K
import lz4repack as L
import restream as RS

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"


def block_payload(data, b, bi):
    p = b["data_start"]
    for j in range(bi):
        p += b["blocks"][j][1]
    csize = b["blocks"][bi][1]
    usize, _, flags = b["blocks"][bi]
    chunk = data[p:p + csize]
    if flags in (2, 3):
        pl, _, _, _, _ = K.lz4_decode(chunk, b"")
        return pl, p, csize
    return chunk, p, csize


def test(fn, bundle_idx, label):
    path = os.path.join(BASE, fn)
    data = open(path, 'rb').read()
    _, bs = K.walk(data=data)
    b = bs[bundle_idx]
    print("=" * 100)
    print("%s  bundle#%d @%d total=%d blocks=%d usize=%d" %
          (fn, bundle_idx, b["start"], b["total"], len(b["blocks"]),
           sum(x[0] for x in b["blocks"])))
    total_ok = 0
    total_case = 0
    for bi in range(len(b["blocks"])):
        pl, cstart, csize = block_payload(data, b, bi)
        if pl is None:
            print("  blk%d 解码失败" % bi)
            continue
        flags = b["blocks"][bi][2]
        ch = data[cstart:cstart + csize]
        for kind in ("str", "pathid", "rand8"):
            # 挑一个真实位置
            if kind == "str":
                idx = pl.find(b"Task_3")
                if idx < 0:
                    idx = pl.find(b"MonoBehaviour")
                tgt = pl[idx:idx + 6]
                new = tgt[:-1] + (b"4" if tgt[-1:] != b"4" else b"5")
            elif kind == "pathid":
                idx = len(pl) // 2
                tgt = pl[idx:idx + 8]
                new = bytes((tgt[0] ^ 0x5A,)) + tgt[1:]
            else:
                idx = len(pl) - 64
                tgt = pl[idx:idx + 8]
                new = bytes(b ^ 0xA5 for b in tgt)
            pn = pl[:idx] + new + pl[idx + len(new):]
            if len(pn) != len(pl):
                print("  长度不等，跳过")
                continue
            total_case += 1
            out, info = RS.rebuild_exact(ch, pn)
            if out is not None and L.decode(out) == pn:
                total_ok += 1
                print("  blk%-3d %-6s pos=%-7d 等长成功 [%s]" %
                      (bi, kind, idx, info["path"]))
            else:
                seqs, stats = RS.restream(ch, pn)
                d = len(L.build([list(s) for s in seqs])) - len(ch)
                print("  blk%-3d %-6s pos=%-7d 失败 差值=%+d %s" %
                      (bi, kind, idx, d, stats))
        if bi >= 5:
            break
    print("  本 bundle 等长成功 %d/%d" % (total_ok, total_case))


test("426491342dde4dcdb8afbb3b895051e6.wmv", 0, "小包")
test("2b869220f02125f5f74351dc3738788e.wmv", 0, "小包")
test("0a95a3510bffb1a31fdef2cae36e8783.wmv", 848, "任务目标包")
