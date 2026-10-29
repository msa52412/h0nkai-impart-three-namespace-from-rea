# -*- coding: utf-8 -*-
"""抽取 Challenge/Task_N 点击前后的完整包序列，判断该卡片的真实语义。"""
import re, sys, io

LOG = r"D:\BH3\7.0\_launch\logs\v2_Server.log"

CLICK = re.compile(r"PlayerLog.*?Challenge/(Task_\d+)/Cover")
# 页面切换 / 包
PAGE = re.compile(r"PlayerLog.*?([A-Za-z0-9_]+PageContext)")
PKT  = re.compile(r"<Packet>\s*(?:\[(\w+)\]\s*)?(.+)$")

def main():
    raw = io.open(LOG, "r", encoding="utf-8", errors="replace").read()
    lines = raw.splitlines()
    # 找所有点击行
    clicks = []
    for i, ln in enumerate(lines):
        m = CLICK.search(ln)
        if m:
            clicks.append((i, m.group(1), ln.strip()[:120]))
    print("点击总数:", len(clicks))
    if not clicks:
        return

    # 对每次点击，打印后续 40 行内的包与页面
    for idx, (i, task, ln) in enumerate(clicks):
        if task not in ("Task_3", "Task_4"):
            continue
        nxt = clicks[idx + 1][0] if idx + 1 < len(clicks) else min(i + 60, len(lines))
        win = lines[i:min(nxt, i + 60)]
        pages, pkts = [], []
        for w in win:
            pm = PAGE.search(w)
            if pm and pm.group(1) not in pages:
                pages.append(pm.group(1))
            km = PKT.search(w)
            if km:
                tag = ("[%s] " % km.group(1)) if km.group(1) else ""
                body = km.group(2).strip()
                if body not in pkts:
                    pkts.append(tag + body[:90])
        print("\n" + "=" * 78)
        print("时间:", ln.split("|")[0].strip() if "|" in ln else "?", " 卡片:", task)
        print("  后续页面:", pages or "(无)")
        print("  后续包:")
        for p in pkts[:14]:
            print("    -", p)

if __name__ == "__main__":
    main()
