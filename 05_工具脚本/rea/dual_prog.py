#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dual_prog.py — 双机并行导出监控 + 自动接力

两台机器的分工是「两头夹」：
    104 从 body_list.txt 头部往后跑（索引 0 → 大）
    105 从尾部往前跑（索引 TOTAL-1 → 小）
所以已覆盖区间永远是 [0, n104) ∪ [TOTAL-n105, TOTAL)，
缺口就是中间那一段 —— 不用下载 tsv，靠 PROGRESS 里的 n 就能算出来。

用法:
    python dual_prog.py            # 打一次快照
    python dual_prog.py -w 30      # 每 30 秒刷新
    python dual_prog.py --handoff  # 若 105 已空闲且仍有缺口，自动派发下一批给它

自动接力做的事：取中间缺口那段地址、倒序、写到 105 的 body_list_round2.txt，
然后重启 105 的 analyzeHeadless（DumpBodies 会按 bodies_b.tsv 里已有的 VA 断点续跑）。
"""
import argparse
import io
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "_pylibs"))
import rsh2

TOTAL = 311382
L104 = dict(bodies="~/re/sym/bodies.tsv", log="~/re/sym/bodies_full.log", host="104")
L105 = dict(bodies="~/re/sym/bodies_b.tsv", log="~/re/sym/bodies_b.log", host="105")

_PROG_RE = re.compile(
    r"PROGRESS (\d+)/(\d+)\s+([\d.]+) 个/秒.*?miss=(\d+) empty=(\d+)")


def snapshot(w):
    """一次往返拿一台机器的指标"""
    cmd = (
        'printf "%%s\\n" "$(wc -l < %s 2>/dev/null || echo 0)";'
        'grep PROGRESS %s 2>/dev/null | tail -2;'
        'printf "%%s\\n" "===MARK===";'
        'printf "%%s\\n" "$(df --output=avail -BG /home | tail -1 | tr -d " G")";'
        'printf "%%s\\n" "$(free -m | awk \'/Mem:/{print $7}\')";'
        'printf "%%s\\n" "$(pgrep -f \'analyzeHead[less]\' | wc -l)"'
        % (w["bodies"], w["log"])
    )
    cli = rsh2.conn(w["host"])
    try:
        rc, out, err = rsh2.run(cli, cmd, 60)
    finally:
        cli.close()
    r = {"lines": 0, "progs": [], "disk": "?", "mem": "?", "alive": 0}
    mark = out.find("===MARK===")
    head = out[:mark] if mark > 0 else out
    tail_ = [x.strip() for x in out[mark + 10:].split("\n") if x.strip()] if mark > 0 else []
    for ln in head.split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        if "PROGRESS" in ln:
            r["progs"].append(ln)
        elif ln.isdigit():
            r["lines"] = int(ln)
    for i, k in enumerate(["disk", "mem", "alive"]):
        if i < len(tail_):
            try:
                r[k] = int(tail_[i]) if k == "alive" else tail_[i]
            except ValueError:
                r[k] = tail_[i]
    return r


STATE = os.path.join(HERE, "_dump", "dual_state.json")


def _load_state():
    try:
        with io.open(STATE, encoding="utf-8") as f:
            d = json.load(f)
    except Exception:
        return {}
    # 清掉旧格式（浮点）和别的键，只保留 104/105 两个采样序列
    out = {}
    for k in ("104", "105"):
        v = d.get(k)
        if isinstance(v, list) and v and isinstance(v[0], list):
            out[k] = v
    return out


def _save_state(st):
    try:
        os.makedirs(os.path.dirname(STATE), exist_ok=True)
        with io.open(STATE, "w", encoding="utf-8") as f:
            json.dump(st, f)
    except Exception:
        pass


def steady_rate(progs):
    """用最后两条 PROGRESS 反推稳态速率（消除加载工程那段固定开销）。

    注意：日志每 500 条才刷一次，相邻两条只差 500 个，短间隔下噪声很大
    （实测同一台机器能读出 9 / 148 两个值）。所以这个值只作为兜底，
    真正显示用 wallclock_rate() 跨进程采样算。
    """
    pts = []
    for ln in progs:
        m = _PROG_RE.search(ln)
        if not m:
            continue
        n, tot, rate, miss, empty = m.groups()
        n, rate, miss, empty = int(n), float(rate), int(miss), int(empty)
        ok = n - miss - empty
        if rate > 0 and ok > 0:
            pts.append((n, ok, ok / rate * 1000.0))
    if len(pts) < 2:
        return None
    (n1, _o1, ms1), (n2, _o2, ms2) = pts[-2], pts[-1]
    dms, dn = ms2 - ms1, n2 - n1
    if dms <= 0 or dn <= 0:
        return None
    return dn / dms * 1000.0


def wallclock_rate(key, n, st, window=600.0):
    """跨两次进程调用算速率。

    做法：留一串 (时间戳, n) 采样，取「窗口内最早的一条」和最新一条求差。
    比单次采样稳得多 —— 单次会被「这一批函数恰好特别大/特别小」带偏
    （实测 104 在 11.6~24.8 摆、105 在 24.1~98.3 摆），
    也比固定条数的中位数稳 —— 中位数在样本少或刚重置时会被坏样本拖住。
    """
    now = time.time()
    pts = st.get(key) or []
    if pts and (not isinstance(pts[0], list)):
        pts = []                       # 旧格式，丢掉
    pts.append([now, n])
    pts = [p for p in pts if now - p[0] <= window * 2]
    st[key] = pts
    if len(pts) < 2:
        return None
    # 窗口内最早的那条
    base = None
    for p in pts:
        if now - p[0] <= window:
            base = p
            break
    if base is None or base is pts[-1]:
        base = pts[0]
    dt = now - base[0]
    dn = n - base[1]
    if dt < 45 or dn <= 0:
        return None
    return dn / dt


def prog_n(progs):
    if not progs:
        return 0
    m = _PROG_RE.search(progs[-1])
    return int(m.group(1)) if m else 0


def bar(frac, width=40):
    k = max(0, min(width, int(frac * width)))
    return "█" * k + "·" * (width - k)


def fmt_secs(s):
    if s is None or s <= 0:
        return "—"
    if s < 3600:
        return "%.0f 分钟" % (s / 60)
    return "%.1f 小时" % (s / 3600)


def report(a104, a105):
    # 日志的 PROGRESS 和 tsv 都有缓冲，两者会互相领先；取大的更接近真实
    # 覆盖量。用 tsv 行数还能让「接力第二轮」之后累计值不受日志被覆盖影响。
    n104 = max(prog_n(a104["progs"]), a104["lines"])
    n105 = max(prog_n(a105["progs"]), a105["lines"])
    st = _load_state()
    r104 = wallclock_rate("104", n104, st) or steady_rate(a104["progs"]) or 0.0
    r105 = wallclock_rate("105", n105, st) or steady_rate(a105["progs"]) or 0.0
    _save_state(st)

    covered = min(TOTAL, n104 + n105)
    gap = TOTAL - covered
    frac = covered / float(TOTAL)

    print("\033[2J\033[H", end="")
    print("═══ 双机并行导出  %s ═══" % time.strftime("%H:%M:%S"))
    print()
    print("  总覆盖  %s  %5.1f%%   %s / %s"
          % (bar(frac), frac * 100, f"{covered:,}", f"{TOTAL:,}"))
    print("          104 头部 %s  ←→  105 尾部 %s"
          % (f"{n104:,}", f"{n105:,}"))
    print()
    print("  ┌─ 104 (Xeon E-2124 / 3核) ─────────────────────────────")
    print("  │  进度 %s / %s   进程 %s   tsv %s 行"
          % (f"{n104:,}", f"{n104 and 310982 or 0:,}",
             "在跑" if a104["alive"] else "已停", f"{a104['lines']:,}"))
    print("  │  速率 %s   磁盘 %s G   可用内存 %s MB"
          % ("%.1f 个/秒" % r104 if r104 else "—", a104["disk"], a104["mem"]))
    print("  └───────────────────────────────────────────────────────")
    print("  ┌─ 105 (Ultra 5 230F / 8核) ────────────────────────────")
    print("  │  进度 %s / 155,691   进程 %s   tsv %s 行"
          % (f"{n105:,}", "在跑" if a105["alive"] else "已停", f"{a105['lines']:,}"))
    print("  │  速率 %s   磁盘 %s G   可用内存 %s MB"
          % ("%.1f 个/秒" % r105 if r105 else "—", a105["disk"], a105["mem"]))
    print("  └───────────────────────────────────────────────────────")
    print()

    if gap <= 0:
        print("  ✅ 无缺口，全部地址已覆盖，可以合并了")
        print("     ssh nas@192.168.0.104 'cat ~/re/sym/bodies.tsv' > bodies_a.tsv")
        print("     ssh nas@192.168.0.105 'cat ~/re/sym/bodies_b.tsv' > bodies_b.tsv")
        print("     cat bodies_a.tsv bodies_b.tsv > bodies_merged.tsv")
        print()
        return n104, n105, gap

    # 104 还会往前拱，105 还会往后拱；两者在中间合拢
    close_speed = r104 + r105
    print("  中间缺口 %s 个（索引 %s .. %s）" % (f"{gap:,}", f"{n104:,}", f"{TOTAL - n105:,}"))
    if close_speed > 0.05:
        print("  合拢速度 %.1f 个/秒  →  约 %s 后全部覆盖"
              % (close_speed, fmt_secs(gap / close_speed)))
    if r104 > 0 and r105 > 0:
        # 104 会在 (TOTAL-n105-n104) 条后撞上 105 的尾巴
        print("  104 单独跑完剩余 %s 需 %s；105 单独跑完 %s 需 %s"
              % (f"{TOTAL - n104:,}", fmt_secs((TOTAL - n104) / r104),
                 f"{155691 - n105:,}", fmt_secs(max(0, 155691 - n105) / r105)))
    print()
    return n104, n105, gap


def handoff(n104, n105, dry=True):
    """105 空闲且有缺口时，把中间缺口那段倒序派给它"""
    head = n104
    tail = TOTAL - n105
    if head >= tail:
        print("  缺口已经闭合，无需派发")
        return False
    lo, hi = head, tail
    src = os.path.join(HERE, "_dump", "body_list.txt")
    if not os.path.exists(src):
        print("  本地缺 _dump/body_list.txt，无法派发")
        return False
    lines = [l.strip() for l in io.open(src, encoding="utf-8", errors="replace") if l.strip()]
    seg = lines[lo:hi][::-1]              # 倒序，从尾部往头部推
    print("  派发区间 [%s, %s) 倒序，共 %s 条" % (f"{lo:,}", f"{hi:,}", f"{len(seg):,}"))
    if dry:
        print("  （dry-run，未实际执行）")
        return False

    local = os.path.join(HERE, "_dump", "body_list_r%d.txt" % int(time.time()))
    io.open(local, "w", newline="\n").write("\n".join(seg) + "\n")
    rsh2.put("105", local, "/home/nas/re/sym/body_list_round.txt")
    print("  已上传 ~/re/sym/body_list_round.txt")

    # 注意：不能用 pkill -f 'analyzeHeadless.*body_list'。
    # 发起命令的 bash 自身命令行里也含这两个词，pkill 会把执行命令的 shell 一起杀掉，
    # paramiko 收到 rc=-1，后续的启动根本没跑（第一次接力就是这么静默失败的）。
    # 改为：上传一个固定的 run_dump.sh，只负责启动；本来 handoff 只在 alive==0 时触发，
    # 没有进程需要清理。
    script = os.path.join(HERE, "_dump", "run_dump.sh")
    if os.path.exists(script):
        rsh2.put("105", script, "/home/nas/re/sym/run_dump.sh")
    cmd = ("sed -i 's/\\r$//' /home/nas/re/sym/run_dump.sh; "
           "chmod +x /home/nas/re/sym/run_dump.sh; "
           "nohup setsid bash /home/nas/re/sym/run_dump.sh "
           "/home/nas/re/sym/body_list_round.txt > /tmp/launch.out 2>&1 < /dev/null & "
           "sleep 6; cat /tmp/launch.out; "
           "pgrep -f analyzeHead[less] | wc -l")
    cli = rsh2.conn("105")
    try:
        rc, o, e = rsh2.run(cli, cmd, 90)
    finally:
        cli.close()
    print("  启动 105: rc=%d %s" % (rc, o.strip().replace("\n", " ")[:100]))
    try:
        os.remove(local)
    except OSError:
        pass
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-w", "--watch", type=int, default=0)
    ap.add_argument("--handoff", action="store_true", help="105 空闲时自动派发下一批")
    ap.add_argument("--dry", action="store_true", help="配 --handoff 只打印不执行")
    ap.add_argument("--log", default=os.path.join(HERE, "_dump", "dual_prog.log"),
                    help="同时写一份到文件（守护模式用）")
    a = ap.parse_args()

    class Tee:
        """同时写 stdout 和日志文件；后台跑时 stdout 会被块缓冲吞掉，靠文件看"""
        def __init__(self, path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.f = io.open(path, "a", encoding="utf-8")

        def write(self, s):
            sys.__stdout__.write(s)
            sys.__stdout__.flush()
            self.f.write(s)
            self.f.flush()

        def flush(self):
            sys.__stdout__.flush()
            self.f.flush()

    if a.watch > 0:
        sys.stdout = Tee(a.log)

    def once():
        a104 = snapshot(L104)
        a105 = snapshot(L105)
        n104, n105, gap = report(a104, a105)
        if a.handoff and gap > 0 and not a105["alive"]:
            print("  105 已空闲 → 尝试接力")
            handoff(n104, n105, dry=a.dry)
        return n104, n105

    if a.watch <= 0:
        once()
        return
    try:
        while True:
            once()
            time.sleep(max(5, a.watch))
    except KeyboardInterrupt:
        print("\n退出")


if __name__ == "__main__":
    main()
