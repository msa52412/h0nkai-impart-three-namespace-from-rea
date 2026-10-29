#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch_scan_icf.py —— 给 scan_this.py 的 main() 加 ICF 跨类型折叠地址过滤"""
import io

path = "scan_this.py"
src = io.open(path, encoding="utf-8").read()

i = src.index("def main():")
j = src.index('if __name__ == "__main__":')

new_main = '''def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "bh3_layout_probe2.tsv"
    dst = sys.argv[2] if len(sys.argv) > 2 else "bh3_layout_obs2.tsv"
    lim = int(sys.argv[3]) if len(sys.argv) > 3 else 0

    # ★ ICF 折叠地址黑名单：一个 RVA 被多个不同 declType 的方法指向时，
    #   该地址扫出的 [this+disp] 属于「某一个」类型，对其它类型全是污染。
    #   典型：0x640CE0（mov rax,[rcx+0x58]; ret）被 20+ 类型的 getter 共用，
    #   WWW 的观测里因此混进了 X509Certificate 的 0x58。同类型共享（重载折叠）无害。
    import csv
    from collections import defaultdict
    here = os.path.dirname(os.path.abspath(__file__))
    mv2 = {r["idx"]: r["declType"] for r in csv.DictReader(
        open(os.path.join(here, "bh3_methods_v2.tsv"), encoding="utf-8", errors="replace"),
        delimiter="\\t")}
    rva_types = defaultdict(set)
    for r in csv.DictReader(
            open(os.path.join(here, "bh3_method_addr.tsv"), encoding="utf-8", errors="replace"),
            delimiter="\\t"):
        if r["rva"].strip():
            rva_types[r["rva"]].add(mv2.get(r["idx"], ""))
    icf_bad = {k for k, v in rva_types.items() if len(v) > 1}
    print("ICF 跨类型折叠地址 %d 个（已排除）" % len(icf_bad))

    out = open(dst, "w", encoding="utf-8")
    out.write("typeIdx\\toffsets\\tnAccess\\tnInsn\\n")
    n = hit = skipped = 0
    import time
    t0 = time.time()
    with open(src, encoding="utf-8", errors="replace") as f:
        next(f)
        for line in f:
            p = line.rstrip("\\n").split("\\t")
            if len(p) < 2:
                continue
            ti = int(p[0])
            n += 1
            if lim and n > lim:
                break
            offs = set()
            nins = 0
            for rs in p[1].split(","):
                rs = rs.strip()
                if not rs:
                    continue
                sr = 0
                if ":" in rs:
                    rs, s2 = rs.split(":", 1)
                    try:
                        sr = int(s2)
                    except ValueError:
                        sr = 0
                if rs.upper() in icf_bad:
                    skipped += 1
                    continue
                try:
                    rva = int(rs, 16)
                except ValueError:
                    continue
                o, k = scan(rva, sr)
                offs |= o
                nins += k
            if offs:
                hit += 1
            out.write("%d\\t%s\\t%d\\t%d\\n" % (
                ti, ",".join("0x%x" % x for x in sorted(offs)), len(offs), nins))
            if n % 5000 == 0:
                out.flush()
                print("  %d  hit=%d  %.1fs" % (n, hit, time.time() - t0))
    out.close()
    print("done: %d 行，有偏移 %d (%.1f%%)  跳过 ICF rva %d 个  %.1fs"
          % (n, hit, 100.0 * hit / max(n, 1), skipped, time.time() - t0))


'''

io.open(path, "w", encoding="utf-8", newline="").write(src[:i] + new_main + src[j:])
print("patched", path)
